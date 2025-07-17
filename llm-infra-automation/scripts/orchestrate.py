from healthcheck import check_ec2_health
from llm_consult import ask_llm
from apply_remediation import apply_ansible_remediation
import os


instances = check_ec2_health()


if instances:
    prompt = f"Instances {instances} are failing health check. What should I do?"

    # We have to prepare a good prompt to let ollama learn the current
    # infrastructure settings, and provided the selections of solutions
    # to pick one to execute

    advice = ask_llm(prompt)
    print("LLM Advice:", advice)
    apply_ansible_remediation("ansible/playbooks/restart_services.yml")
else:
    print("All instances are healthy.")


def aggregate_terraform(directory: str = "../../terraform") -> str:
    tf_contents = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".tf"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    tf_contents.append(f"\n# ===== {file} =====\n" + f.read())
    return "\n".join(tf_contents)
