# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for snapshotting disks."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import name_generator
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import resources


class SnapshotDisks(base_classes.BaseAsyncMutator):
  """Snapshot Google Compute Engine disks."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--description',
        help=('An optional, textual description for the snapshots being '
              'created.'))

    snapshot_names = parser.add_argument(
        '--snapshot-names',
        metavar='SNAPSHOT_NAME',
        nargs='+',
        help='Names to assign to the snapshots.')
    snapshot_names.detailed_help = """\
        Names to assign to the snapshots. Without this option, the
        name of each snapshot will be a random, 16-character
        hexadecimal number that starts with a letter. The values of
        this option run parallel to the disks specified. For example,
        +
          $ {command} my-disk-1 my-disk-2 my-disk-3 \\
              --snapshot-name snapshot-1 snapshot-2 snapshot-3
        +
        will result in ``my-disk-1'' being snapshotted as
        ``snapshot-1'', ``my-disk-2'' as ``snapshot-2'', and so on.
        """

    parser.add_argument(
        'disk_names',
        metavar='DISK_NAME',
        nargs='+',
        help='The names of the disks to snapshot.')

    utils.AddZoneFlag(
        parser,
        resource_type='disks',
        operation_type='snapshot')

  @property
  def service(self):
    return self.context['compute'].disks

  @property
  def custom_get_requests(self):
    return self._target_to_get_request

  @property
  def method(self):
    return 'CreateSnapshot'

  @property
  def resource_type(self):
    return 'snapshots'

  @property
  def prompting_resource_type(self):
    return 'disks'

  def CreateRequests(self, args):
    """Returns a list of requests necessary for snapshotting disks."""
    if args.snapshot_names:
      if len(args.disk_names) != len(args.snapshot_names):
        raise exceptions.ToolException(
            '[--snapshot-names] must have the same number of values as disks '
            'being snapshotted.')
      snapshot_names = args.snapshot_names
    else:
      # Generates names like "d52jsqy3db4q".
      snapshot_names = [name_generator.GenerateRandomName()
                        for _ in args.disk_names]

    snapshot_refs = [
        resources.Parse(snapshot_name, collection='compute.snapshots')
        for snapshot_name in snapshot_names]

    self._target_to_get_request = {}

    requests = []
    disk_refs = self.CreateZonalReferences(args.disk_names, args.zone)

    for disk_ref, snapshot_ref in zip(disk_refs, snapshot_refs):
      request = messages.ComputeDisksCreateSnapshotRequest(
          disk=disk_ref.Name(),
          snapshot=messages.Snapshot(
              name=snapshot_ref.Name(),
              description=args.description,
          ),
          project=self.context['project'],
          zone=disk_ref.zone)
      requests.append(request)

      self._target_to_get_request[disk_ref.SelfLink()] = (
          snapshot_ref.SelfLink(),
          self.context['compute'].snapshots,
          messages.ComputeSnapshotsGetRequest(
              snapshot=snapshot_ref.Name(),
              project=self.context['project']))

    return requests


SnapshotDisks.detailed_help = {
    'brief': 'Snapshot Google Compute Engine persistent disks',
    'DESCRIPTION': """\
        *{command}* creates snapshots of persistent disks. Snapshots
        are useful for backing up data or copying a persistent disk.
        """,
}
