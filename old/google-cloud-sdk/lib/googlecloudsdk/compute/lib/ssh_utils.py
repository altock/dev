# Copyright 2014 Google Inc. All Rights Reserved.

"""Utilities for subcommands that need to SSH into virtual machine guests."""
import logging
import os
import subprocess

from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import metadata_utils
from googlecloudsdk.compute.lib import path_simplifier
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import time_utils
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import files

# The maximum amount of time to wait for a newly-added SSH key to
# propagate before giving up.
_SSH_KEY_PROPAGATION_TIMEOUT_SEC = 60


def UserHost(user, host):
  """Returns a string of the form user@host."""
  if user:
    return user + '@' + host
  else:
    return host


def GetExternalIPAddress(instance_resource, no_raise=False):
  """Returns the external IP address of the instance.

  Args:
    instance_resource: An instance resource object.
    no_raise: A boolean flag indicating whether or not to return None instead of
      raising.

  Raises:
    ToolException: If no external IP address is found for the instance_resource
      and no_raise is False.

  Returns:
    A string IP or None is no_raise is True and no ip exists.
  """
  if instance_resource.networkInterfaces:
    access_configs = instance_resource.networkInterfaces[0].accessConfigs
    if access_configs:
      ip_address = access_configs[0].natIP
      if ip_address:
        return ip_address
      elif not no_raise:
        raise exceptions.ToolException(
            'Instance [{0}] in zone [{1}] has not been allocated an external '
            'IP address yet. Try rerunning this command later.'.format(
                instance_resource.name,
                path_simplifier.Name(instance_resource.zone)))

  if no_raise:
    return None

  raise exceptions.ToolException(
      'Instance [{0}] in zone [{1}] does not have an external IP address, '
      'so you cannot SSH into it. To add an external IP address to the '
      'instance, use [gcloud compute instances add-access-config].'
      .format(instance_resource.name,
              path_simplifier.Name(instance_resource.zone)))


def _RunExecutable(cmd_args):
  try:
    subprocess.check_call(cmd_args)
  except OSError as e:
    raise exceptions.ToolException(
        '[{0}] exited with [{1}].'.format(cmd_args[0], e.strerror))
  except subprocess.CalledProcessError as e:
    raise exceptions.ToolException(
        '[{0}] exited with return code [{1}].'
        .format(cmd_args[0], e.returncode))


def _GetSSHKeysFromMetadata(metadata):
  """Returns the value of the "sshKeys" metadata as a list."""
  if not metadata:
    return []
  for item in metadata.items:
    if item.key == constants.SSH_KEYS_METADATA_KEY:
      return [key.strip() for key in item.value.split('\n') if key]
  return []


def _PrepareSSHKeysValue(ssh_keys):
  """Returns a string appropriate for the metadata.

  Values from are taken from the tail until either all values are
  taken or _MAX_METADATA_VALUE_SIZE_IN_BYTES is reached, whichever
  comes first. The selected values are then reversed. Only values at
  the head of the list will be subject to removal.

  Args:
    ssh_keys: A list of keys. Each entry should be one key.

  Returns:
    A new-line-joined string of SSH keys.
  """
  keys = []
  bytes_consumed = 0

  for key in reversed(ssh_keys):
    num_bytes = len(key + '\n')
    if bytes_consumed + num_bytes > constants.MAX_METADATA_VALUE_SIZE_IN_BYTES:
      log.warn('The following SSH key will be removed from your project '
               'because your sshKeys metadata value has reached its '
               'maximum allowed size of {0} bytes: {1}'
               .format(constants.MAX_METADATA_VALUE_SIZE_IN_BYTES, key))
    else:
      keys.append(key)
      bytes_consumed += num_bytes

  keys.reverse()
  return '\n'.join(keys)


def _AddSSHKeyToMetadataMessage(user, public_key, metadata):
  """Adds the public key material to the metadata if it's not already there."""
  entry = '{user}:{public_key}'.format(
      user=user, public_key=public_key)

  ssh_keys = _GetSSHKeysFromMetadata(metadata)
  log.debug('Current SSH keys in project: {0}'.format(ssh_keys))

  if entry in ssh_keys:
    return metadata
  else:
    ssh_keys.append(entry)
    return metadata_utils.ConstructMetadataMessage(
        metadata={
            constants.SSH_KEYS_METADATA_KEY: _PrepareSSHKeysValue(ssh_keys)},
        existing_metadata=metadata)


class BaseSSHCommand(base_classes.BaseCommand):
  """Base class for subcommands that need to connect to instances using SSH.

  Subclasses can call EnsureSSHKeyIsInProject() to make sure that the
  user's public SSH key is placed in the project metadata before
  proceeding.
  """

  @staticmethod
  def Args(parser):
    ssh_key_file = parser.add_argument(
        '--ssh-key-file',
        help='The path to the SSH key file.')
    ssh_key_file.detailed_help = """\
        The path to the SSH key file. By deault, this is ``{0}''.
        """.format(constants.DEFAULT_SSH_KEY_FILE)

  def GetProject(self):
    """Returns the project object."""
    objects = list(request_helper.MakeRequests(
        requests=[(self.context['compute'].projects,
                   'Get',
                   messages.ComputeProjectsGetRequest(
                       project=properties.VALUES.core.project.Get(
                           required=True),
                   ))],
        http=self.context['http'],
        batch_url=self.context['batch-url']))
    return objects[0]

  def SetProjectMetadata(self, new_metadata):
    """Sets the project metadata to the new metadata."""
    compute = self.context['compute']

    list(request_helper.MakeRequests(
        requests=[(compute.projects,
                   'SetCommonInstanceMetadata',
                   messages.ComputeProjectsSetCommonInstanceMetadataRequest(
                       metadata=new_metadata,
                       project=properties.VALUES.core.project.Get(
                           required=True),
                   ))],
        http=self.context['http'],
        batch_url=self.context['batch-url']))

  def EnsureSSHKeyIsInProject(self, user):
    """Ensures that the user's public SSH key is in the project metadata."""
    # First, grab the public key from the user's computer. If the
    # public key doesn't already exist, GetPublicKey() should create
    # it.
    public_key = self.GetPublicKey()

    # Second, let's make sure the public key is in the project metadata.
    project = self.GetProject()
    existing_metadata = project.commonInstanceMetadata
    new_metadata = _AddSSHKeyToMetadataMessage(
        user, public_key, existing_metadata)
    if new_metadata != existing_metadata:
      self.SetProjectMetadata(new_metadata)

  def GetPublicKey(self):
    """Generates an SSH key using ssh-key (if necessary) and returns it."""
    public_ssh_key_file = self.ssh_key_file + '.pub'
    if (not os.path.exists(self.ssh_key_file) or
        not os.path.exists(public_ssh_key_file)):
      log.warn('You do not have an SSH key for Google Compute Engine.')
      log.warn('[%s] will be executed to generate a key.',
               self.ssh_keygen_executable)

      ssh_directory = os.path.dirname(public_ssh_key_file)
      if not os.path.exists(ssh_directory):
        if console_io.PromptContinue(
            'This tool needs to create the directory [{0}] before being able '
            'to generate SSH keys.'.format(ssh_directory)):
          files.MakeDir(ssh_directory, 0700)
        else:
          raise exceptions.ToolException('SSH key generation aborted by user.')

      keygen_args = [
          self.ssh_keygen_executable,
          '-t', 'rsa',
          '-f', self.ssh_key_file,
          ]
      _RunExecutable(keygen_args)

    with open(public_ssh_key_file) as f:
      return f.readline().strip()

  @property
  def resource_type(self):
    return 'instances'

  def Run(self, args):
    """Subclasses must call this in their Run() before continuing."""
    self.scp_executable = files.FindExecutableOnPath('scp')
    self.ssh_executable = files.FindExecutableOnPath('ssh')
    self.ssh_keygen_executable = files.FindExecutableOnPath('ssh-keygen')
    if (not self.scp_executable or
        not self.ssh_executable or
        not self.ssh_keygen_executable):
      raise exceptions.ToolException('Your platform does not support OpenSSH.')

    self.ssh_key_file = os.path.realpath(os.path.expanduser(
        args.ssh_key_file or constants.DEFAULT_SSH_KEY_FILE))


class BaseSSHCLICommand(BaseSSHCommand):
  """Base class for subcommands that use ssh or scp."""

  @staticmethod
  def Args(parser):
    BaseSSHCommand.Args(parser)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help=('If provided, prints the command that would be run to standard '
              'out instead of executing it.'))

    plain = parser.add_argument(
        '--plain',
        action='store_true',
        help='Suppresses the automatic addition of ssh/scp flags.')
    plain.detailed_help = """\
        Suppresses the automatic addition of *ssh(1)*/*scp(1)* flags. This flag
        is useful if you want to take care of authentication yourself or
        re-enable strict host checking.
        """

  def GetDefaultFlags(self):
    """Returns a list of default commandline flags."""
    return [
        '-i', self.ssh_key_file,
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'CheckHostIP=no',
        '-o', 'StrictHostKeyChecking=no',
        ]

  def GetInstanceExternalIpAddress(self, instance_ref):
    """Returns the external ip address for the given instance."""
    request = (self.context['compute'].instances,
               'Get',
               messages.ComputeInstancesGetRequest(
                   instance=instance_ref.Name(),
                   project=self.context['project'],
                   zone=instance_ref.zone))

    objects = list(request_helper.MakeRequests(
        requests=[request],
        http=self.context['http'],
        batch_url=self.context['batch-url']))

    return GetExternalIPAddress(objects[0])

  def WaitUntilSSHable(self, user, external_ip_address):
    """Blocks until SSHing to the given host succeeds."""
    ssh_args_for_polling = [self.ssh_executable]
    ssh_args_for_polling.extend(self.GetDefaultFlags())
    ssh_args_for_polling.append(UserHost(user, external_ip_address))
    ssh_args_for_polling.append('true')

    start_sec = time_utils.CurrentTimeSec()
    while True:
      logging.debug('polling instance for SSHability')
      retval = subprocess.call(ssh_args_for_polling)
      if retval == 0:
        break
      if (time_utils.CurrentTimeSec() - start_sec >
          _SSH_KEY_PROPAGATION_TIMEOUT_SEC):
        raise exceptions.ToolException(
            'Your SSH key has not propagated to your instance yet. '
            'Try running this command again.')
      time_utils.Sleep(5)

  def ActuallyRun(self, args, cmd_args, user, external_ip_address):
    """Run the command specified in cmd_args."""
    if args.dry_run:
      log.out.Print(' '.join(cmd_args))
      return

    self.EnsureSSHKeyIsInProject(user)
    self.WaitUntilSSHable(user, external_ip_address)

    logging.debug('%s command: %s', cmd_args[0], ' '.join(cmd_args))

    _RunExecutable(cmd_args)
