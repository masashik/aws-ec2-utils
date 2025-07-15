import subprocess

def apply_ansible_remediation(playbook):
    try:
        result = subprocess.run(
            ["ansible-playbook", playbook],
            capture_output=True,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except Exception as e:
        print("Failed to run remediation playbook:", e)

if __name__ == "__main__":
    playbook_path = "ansible/playbooks/restart_services.yml"
    apply_ansible_remediation(playbook_path)
