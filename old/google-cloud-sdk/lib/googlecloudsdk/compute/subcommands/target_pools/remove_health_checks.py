# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing health checks from target pools."""
from googlecloudapis.compute.v1 import compute_v1_messages as messages
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import resources


class RemoveHealthChecks(base_classes.BaseAsyncMutator):
  """Remove a health check from a target pool."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--http-health-check',
        help=('Specifies an HTTP health check object to remove from the '
              'target pool.'),
        metavar='HEALTH_CHECK',
        required=True)

    utils.AddRegionFlag(
        parser,
        resource_type='target pool',
        operation_type='remove health checks from')

    parser.add_argument(
        'name',
        help=('The name of the target pool from which to remove the '
              'health check.'))

  @property
  def service(self):
    return self.context['compute'].targetPools

  @property
  def method(self):
    return 'RemoveHealthCheck'

  @property
  def resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    http_health_check_ref = resources.Parse(
        args.http_health_check, collection='compute.httpHealthChecks')

    target_pool_ref = self.CreateRegionalReference(args.name, args.region)
    request = messages.ComputeTargetPoolsRemoveHealthCheckRequest(
        region=target_pool_ref.region,
        project=self.context['project'],
        targetPool=target_pool_ref.Name(),
        targetPoolsRemoveHealthCheckRequest=(
            messages.TargetPoolsRemoveHealthCheckRequest(
                healthChecks=[messages.HealthCheckReference(
                    healthCheck=http_health_check_ref.SelfLink())])))

    return [request]


RemoveHealthChecks.detailed_help = {
    'brief': 'Remove an HTTP health check from a target pool',
    'DESCRIPTION': """\
        *{command}* is used to remove an HTTP health check
        from a target pool. Health checks are used to determine
        the health status of instances in the target pool. For more
        information on health checks and load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].
        """,
}
