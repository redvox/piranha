from piranha.client import get_client


def get_autoscaling_groups():
    ec2_client = get_client('autoscaling')
    asgs = []
    params = {}
    while True:
        response = ec2_client.describe_auto_scaling_groups(**params)
        if not response:
            raise Exception('failed to describe autoscaling groups')

        asgs.extend(response['AutoScalingGroups'])
        if 'NextToken' not in response:
            break
        params['NextToken'] = response['NextToken']

    return asgs


def get_autoscaling_group_by_name(name):
    ec2_client = get_client('autoscaling')
    response = ec2_client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[name],
        MaxRecords=1
    )
    if not response:
        return None
    if len(response['AutoScalingGroups']) == 0:
        return None
    return response['AutoScalingGroups'][0]


def discover(exclude_tags={}):
    asgs = get_autoscaling_groups()
    services = []

    for asg in asgs:
        info = _extract_tags(asg)
        if _should_exclude(exclude_tags, info):
            continue
        info['asg'] = asg['AutoScalingGroupName']
        info['elb'] = asg.get('LoadBalancerNames', [None])[0]
        services.append(info)
    return services


def _extract_tags(asg):
    if 'Tags' not in asg:
        return {}
    return {tag['Key']: tag['Value'] for tag in asg['Tags']}


def _should_exclude(exclude_tags, tags):
    return any(item in tags.items() for item in exclude_tags.items())
