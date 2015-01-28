"""Generated message classes for autoscaler version v1beta2.

The Google Compute Engine Autoscaler API provides autoscaling for groups of
Cloud VMs.
"""

from protorpc import messages


package = 'autoscaler'


class Autoscaler(messages.Message):
  """Cloud Autoscaler resource.

  Fields:
    autoscalingPolicy: Configuration parameters for autoscaling algorithm.
    creationTimestamp: [Output Only] Creation timestamp in RFC3339 text
      format.
    description: An optional textual description of the resource provided by
      the client.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    name: Name of the Autoscaler resource. Must be unique per project and
      zone.
    selfLink: [Output Only] A self-link to the Autoscaler configuration
      resource.
    target: URL to the entity which will be autoscaled. Currently the only
      supported value is ReplicaPool?s URL. Note: it is illegal to specify
      multiple Autoscalers for the same target.
  """

  autoscalingPolicy = messages.MessageField('AutoscalingPolicy', 1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  name = messages.StringField(5)
  selfLink = messages.StringField(6)
  target = messages.StringField(7)


class AutoscalerAutoscalersDeleteRequest(messages.Message):
  """A AutoscalerAutoscalersDeleteRequest object.

  Fields:
    autoscaler: Name of the Autoscaler resource.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  autoscaler = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class AutoscalerAutoscalersGetRequest(messages.Message):
  """A AutoscalerAutoscalersGetRequest object.

  Fields:
    autoscaler: Name of the Autoscaler resource.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  autoscaler = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class AutoscalerAutoscalersInsertRequest(messages.Message):
  """A AutoscalerAutoscalersInsertRequest object.

  Fields:
    autoscaler: A Autoscaler resource to be passed as the request body.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  autoscaler = messages.MessageField('Autoscaler', 1)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class AutoscalerAutoscalersListRequest(messages.Message):
  """A AutoscalerAutoscalersListRequest object.

  Fields:
    filter: A string attribute.
    maxResults: A integer attribute.
    pageToken: A string attribute.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class AutoscalerAutoscalersPatchRequest(messages.Message):
  """A AutoscalerAutoscalersPatchRequest object.

  Fields:
    autoscaler: Name of the Autoscaler resource.
    autoscalerResource: A Autoscaler resource to be passed as the request
      body.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  autoscaler = messages.StringField(1, required=True)
  autoscalerResource = messages.MessageField('Autoscaler', 2)
  project = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class AutoscalerAutoscalersUpdateRequest(messages.Message):
  """A AutoscalerAutoscalersUpdateRequest object.

  Fields:
    autoscaler: Name of the Autoscaler resource.
    autoscalerResource: A Autoscaler resource to be passed as the request
      body.
    project: Project ID of Autoscaler resource.
    zone: Zone name of Autoscaler resource.
  """

  autoscaler = messages.StringField(1, required=True)
  autoscalerResource = messages.MessageField('Autoscaler', 2)
  project = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class AutoscalerListResponse(messages.Message):
  """A AutoscalerListResponse object.

  Fields:
    items: Autoscaler resources.
    nextPageToken: [Output only] A token used to continue a truncated list
      request.
  """

  items = messages.MessageField('Autoscaler', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class AutoscalerZoneOperationsDeleteRequest(messages.Message):
  """A AutoscalerZoneOperationsDeleteRequest object.

  Fields:
    operation: A string attribute.
    project: A string attribute.
    zone: A string attribute.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class AutoscalerZoneOperationsDeleteResponse(messages.Message):
  """An empty AutoscalerZoneOperationsDelete response."""


class AutoscalerZoneOperationsGetRequest(messages.Message):
  """A AutoscalerZoneOperationsGetRequest object.

  Fields:
    operation: A string attribute.
    project: A string attribute.
    zone: A string attribute.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class AutoscalerZoneOperationsListRequest(messages.Message):
  """A AutoscalerZoneOperationsListRequest object.

  Fields:
    filter: A string attribute.
    maxResults: A integer attribute.
    pageToken: A string attribute.
    project: A string attribute.
    zone: A string attribute.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class AutoscalingPolicy(messages.Message):
  """Cloud Autoscaler policy.

  Fields:
    coolDownPeriodSec: The number of seconds that the Autoscaler should wait
      between two succeeding changes to the number of virtual machines. You
      should define an interval that is at least as long as the initialization
      time of a virtual machine and the time it may take for replica pool to
      create the virtual machine. The default is 60 seconds.
    cpuUtilization: Configuration parameters of CPU based autoscaling policy.
    maxNumReplicas: The maximum number of replicas that the Autoscaler can
      scale up to.
    minNumReplicas: The minimum number of replicas that the Autoscaler can
      scale down to.
  """

  coolDownPeriodSec = messages.IntegerField(1, variant=messages.Variant.INT32)
  cpuUtilization = messages.MessageField('AutoscalingPolicyCpuUtilization', 2)
  maxNumReplicas = messages.IntegerField(3, variant=messages.Variant.INT32)
  minNumReplicas = messages.IntegerField(4, variant=messages.Variant.INT32)


class AutoscalingPolicyCpuUtilization(messages.Message):
  """CPU utilization policy.

  Fields:
    utilizationTarget: The target utilization that the Autoscaler should
      maintain. Must be a float value between (0, 1]. If not defined, the
      default is 0.8.
  """

  utilizationTarget = messages.FloatField(1)


class Operation(messages.Message):
  """A Operation object.

  Messages:
    ErrorValue: A ErrorValue object.
    WarningsValueListEntry: A WarningsValueListEntry object.

  Fields:
    clientOperationId: A string attribute.
    creationTimestamp: A string attribute.
    endTime: A string attribute.
    error: A ErrorValue attribute.
    httpErrorMessage: A string attribute.
    httpErrorStatusCode: A integer attribute.
    id: A string attribute.
    insertTime: A string attribute.
    kind: Type of the resource.
    name: A string attribute.
    operationType: A string attribute.
    progress: A integer attribute.
    region: A string attribute.
    selfLink: A string attribute.
    startTime: A string attribute.
    status: A string attribute.
    statusMessage: A string attribute.
    targetId: A string attribute.
    targetLink: A string attribute.
    user: A string attribute.
    warnings: A WarningsValueListEntry attribute.
    zone: A string attribute.
  """

  class ErrorValue(messages.Message):
    """A ErrorValue object.

    Messages:
      ErrorsValueListEntry: A ErrorsValueListEntry object.

    Fields:
      errors: A ErrorsValueListEntry attribute.
    """

    class ErrorsValueListEntry(messages.Message):
      """A ErrorsValueListEntry object.

      Fields:
        code: A string attribute.
        location: A string attribute.
        message: A string attribute.
      """

      code = messages.StringField(1)
      location = messages.StringField(2)
      message = messages.StringField(3)

    errors = messages.MessageField('ErrorsValueListEntry', 1, repeated=True)

  class WarningsValueListEntry(messages.Message):
    """A WarningsValueListEntry object.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: A string attribute.
      data: A DataValueListEntry attribute.
      message: A string attribute.
    """

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A string attribute.
        value: A string attribute.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.StringField(1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  clientOperationId = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  endTime = messages.StringField(3)
  error = messages.MessageField('ErrorValue', 4)
  httpErrorMessage = messages.StringField(5)
  httpErrorStatusCode = messages.IntegerField(6, variant=messages.Variant.INT32)
  id = messages.IntegerField(7, variant=messages.Variant.UINT64)
  insertTime = messages.StringField(8)
  kind = messages.StringField(9, default=u'autoscaler#operation')
  name = messages.StringField(10)
  operationType = messages.StringField(11)
  progress = messages.IntegerField(12, variant=messages.Variant.INT32)
  region = messages.StringField(13)
  selfLink = messages.StringField(14)
  startTime = messages.StringField(15)
  status = messages.StringField(16)
  statusMessage = messages.StringField(17)
  targetId = messages.IntegerField(18, variant=messages.Variant.UINT64)
  targetLink = messages.StringField(19)
  user = messages.StringField(20)
  warnings = messages.MessageField('WarningsValueListEntry', 21, repeated=True)
  zone = messages.StringField(22)


class OperationList(messages.Message):
  """A OperationList object.

  Fields:
    id: A string attribute.
    items: A Operation attribute.
    kind: Type of resource.
    nextPageToken: A string attribute.
    selfLink: A string attribute.
  """

  id = messages.StringField(1)
  items = messages.MessageField('Operation', 2, repeated=True)
  kind = messages.StringField(3, default=u'autoscaler#operationList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class StandardQueryParameters(messages.Message):
  """Query parameters accepted by all methods.

  Enums:
    AltValueValuesEnum: Data format for the response.

  Fields:
    alt: Data format for the response.
    fields: Selector specifying which fields to include in a partial response.
    key: API key. Your API key identifies your project and provides you with
      API access, quota, and reports. Required unless you provide an OAuth 2.0
      token.
    oauth_token: OAuth 2.0 token for the current user.
    prettyPrint: Returns response with indentations and line breaks.
    quotaUser: Available to use for quota purposes for server-side
      applications. Can be any arbitrary string assigned to a user, but should
      not exceed 40 characters. Overrides userIp if both are provided.
    trace: A tracing token of the form "token:<tokenid>" or "email:<ldap>" to
      include in api requests.
    userIp: IP address of the site where the request originates. Use this if
      you want to enforce per-user limits.
  """

  class AltValueValuesEnum(messages.Enum):
    """Data format for the response.

    Values:
      json: Responses with Content-Type of application/json
    """
    json = 0

  alt = messages.EnumField('AltValueValuesEnum', 1, default=u'json')
  fields = messages.StringField(2)
  key = messages.StringField(3)
  oauth_token = messages.StringField(4)
  prettyPrint = messages.BooleanField(5, default=True)
  quotaUser = messages.StringField(6)
  trace = messages.StringField(7)
  userIp = messages.StringField(8)

