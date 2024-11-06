from boto3 import client
from moto import mock_aws


def print_task(n):
    print(f"\033[4mTask {n}\033[0m")


@mock_aws
def warm_up():
    print_task(1)
    s3 = client("s3")
    bucket_name = "warmup_bucket"
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-2",
        },
    )
    print_task(2)
    for i in range(2):
        file = f"file{i+1}.txt"
        with open(f"warmup_files/{file}") as f:
            content = f.read()
            s3.put_object(Bucket=bucket_name, Key=file, Body=content)

    print_task(3)
    dir_list = []
    for key in s3.list_objects(Bucket=bucket_name)["Contents"]:
        dir_list.append(key["Key"])
    print(f"The s3 bucket contains {' and '.join(dir_list)}.")

    print_task(4)
    content = (
        s3.get_object(Bucket=bucket_name, Key=dir_list[0])["Body"]
        .read()
        .decode("utf-8")
    )
    print(f"Contents of {dir_list[0]}: {content}")

    print_task(5)
    response = s3.delete_objects(
        Bucket=bucket_name,
        Delete={
            "Objects": [{"Key": filename} for filename in dir_list],
            "Quiet": False,
        },
    )
    print(f"Deleted files: {response['Deleted']}")
    # print(s3.list_objects(Bucket=bucket_name))

    print_task(6)
    s3.delete_bucket(Bucket=bucket_name)

    print_task(7)
    print(f"Buckets: {s3.list_buckets()['Buckets']}")


if __name__ == "__main__":
    warm_up()
