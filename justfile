vm_user := "debian"
vm_password := "debian"
vm_ip := "192.168.64.5"

SSH := "sshpass -p {{vm_password}} ssh {{vm_user}}@{{vm_ip}}"
SCP := ""


command cmd="":
    sshpass -p {{vm_password}} ssh -t {{vm_user}}@{{vm_ip}} {{cmd}}

copy src dst:
    sshpass -p {{vm_password}} scp -r {{src}} {{dst}}

connect:
    just command

deploy:
    just copy src {{vm_user}}@{{vm_ip}}:~/src

return:
    just command "mkdir -p \~/out"
    just copy {{vm_user}}@{{vm_ip}}:~/out .

clean:
    just command 'rm -rf \~/src \~/out'

poc: clean deploy
    just command '\~/.local/bin/uv run /home/{{vm_user}}/src/poc.py'
    just return

posh: clean deploy
    just command 'chmod +x /home/{{vm_user}}/src/poc.sh'
    just command '/home/{{vm_user}}/src/poc.sh'
    just return

shellcode:
    uv run shellcodes/build.py
