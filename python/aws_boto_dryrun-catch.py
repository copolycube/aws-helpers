"""
Some generic code we're repeating often to catch dry-run executions.
"""
from botocore.exceptions import ClientError

DryRun = True
# DryRun = False

delete_ok = 0
delete_ko = 0


def operation(toto):
    return


try:
    operation(DryRun=DryRun)
except ClientError as e:
    if e.response['Error']['Code'] == 'DryRunOperation':
        print("OK {}  DryRunOperation : Delete request would have succeeded, but DryRun flag is set".format(
            "test"))
        delete_ok += 1
    elif e.response['Error']['Code'] == 'UnauthorizedOperation':
        print(
            "KO {} UnauthorizedOperation : delete request would have FAILED, DryRun flag is set anyway".format(
                "test"))
        delete_ko += 1
    else:
        print("KO {} Unexpected error: {}".format("test", e))
        delete_ko += 1

print("Was it a Dry Run ?  {}".format(DryRun))
print("delete_ok: {}".format(delete_ok))
print("delete_ko: {}".format(delete_ko))
