import boto3

client = boto3.client("ec2")

"""
Todos:
    - Terminate instance
    - Check instance for shutdown warning
    - Attach volume
"""


class Server:

    """
    todos:
        - async start & stop methods
        - send commands with ssh
    """

    def __init__(self, params):

        self.params = params
        self._instance = None

    @property
    def instance(self):
        if self._instance:
            return self._instance

        active_instances = boto3.resource(
            "ec2", self.params["AvailabilityZone"]
        ).instances.filter(
            Filters=[
                {"Name": "instance-state-name", "Values": ["pending", "running"]},
                {"Name": "tag:Name", "Values": [self.params["TagValue"]]},
            ]
        )
        active_instances = [instance for instance in active_instances]
        if active_instances:
            return active_instances[0]
        else:
            return None

    def start_instance(self):

        if self.instance:
            raise ValueError("Instance already exists")

        DryRun = self.params.get("DryRun")
        ClientToken = self.params.get("ClientToken")
        LaunchSpecification = self.params["LaunchSpecification"]
        SpotPrice = self.params["SpotPrice"]

        Device = self.params["Device"]
        VolumeId = self.params["VolumeId"]

        instance_id = self._submit_spot_request(
            DryRun, ClientToken, LaunchSpecification, SpotPrice
        )

        self._instance = boto3.resource("ec2").Instance(instance_id)
        self._instance.create_tags(
            Tags=[{"Key": "Name", "Value": self.params["TagValue"]}]
        )
        self._instance.wait_until_running()

        self._instance.attach_volume(Device=Device, VolumeId=VolumeId)

    def _submit_spot_request(self, DryRun, ClientToken, LaunchSpecification, SpotPrice):

        client = boto3.client("ec2")

        request_response = client.request_spot_instances(
            DryRun=DryRun,
            # ClientToken = ClientToken,
            LaunchSpecification=LaunchSpecification,
            SpotPrice=SpotPrice,
        )

        sir_id = request_response["SpotInstanceRequests"][0]["SpotInstanceRequestId"]

        while True:
            try:
                request_metadata = client.describe_spot_instance_requests(
                    SpotInstanceRequestIds=[sir_id]
                )["SpotInstanceRequests"][0]
            except:
                continue
            if "InstanceId" in request_metadata:
                break
            else:
                continue

        return request_metadata["InstanceId"]

    def terminate(self):
        if self.instance:
            try:
                self.instance.terminate()
                self._instance = None
            except Exception as e:
                raise e
        else:
            raise ValueError("No instance running")


if __name__ == "__main__":

    import params

    server = Server(params.ec2_params)
    server.start_instance()
