from healthcheck import check_ec2_health
from llm_consult import ask_llm_for_action
from apply_remediation import apply_ansible_remediation
import os
import boto3


def restart_server(instance_id, region="ca-central-1"):
    ec2 = boto3.client("ec2", region_name=region)
    ec2.reboot_instances(InstanceIds=[instance_id])
    #ec2.start_instances(InstanceIds=instance_ids, DryRun=dry_run)


def main():
    print("Running EC2 health checks...")
    results = check_ec2_health()

    for r in results:
        print(f"Instance {r['instance_id']} — State: {r['state']} | Status: {r['status']} | CPU: {r['avg_cpu']}%")

        # Example condition: unhealthy + low CPU = maybe hung
        if r["status"] != "ok" and r["avg_cpu"] < 10:
            print(f"Instance {r['instance_id']} may be unhealthy. Asking LLM...")
            decision = ask_llm_for_action(r)  # Expected output: "restart" or "ignore"

            import sys
            print("=========================================================")
            print(decision)
            print("=========================================================")
            sys.stdout.flush()

            if decision == "restart":
                print(f"Restarting {r['instance_id']}...")
                restart_server(r["instance_id"])
                # execute ansible restart playbook.
                apply_ansible_remediation()
            else:
                print(f"LLM said no action needed for {r['instance_id']}.")
        elif r["status"] == "ok" and r["avg_cpu"] > 70:
            print(f"Instance {r['instance_id']} having too much load and may be unhealthy. Asking LLM...")
            decision = ask_llm_for_action(r)  # Expected output: "restart" or "ignore"
            import sys
            print("=========================================================")
            print(decision)
            print("=========================================================")
            sys.stdout.flush()

            if decision == "restart":
                print(f"Restarting {r['instance_id']}...")
                restart_server(r["instance_id"])
                # execute ansible restart playbook.
            else:
                print(f"LLM said no action needed for {r['instance_id']}.")
        else:
            print(f"LLM said no action needed for {r['instance_id']}.")

if __name__ == "__main__":
    main()
