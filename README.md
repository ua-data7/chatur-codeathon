# Chatur

#commands to install on local host

#this was tested on
```
PRETTY_NAME="Ubuntu 22.04.1 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.1 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy
```
**Steps (Note:These instructions won't work on an Apple m1 mac.)
  
- Install docker with  [docker compose](https://docs.docker.com/compose/install/).
- git clone https://github.com/ua-data7/chatur-codeathon
- cd propeller/langserve
- docker compose --file docker-compose.yml --project-name "chatur" build
- docker compose --file docker-compose.yml --project-name "chatur" up -d
- docker compose --file docker-compose.yml --project-name "chatur" exec ollama ollama pull mistral
- curl https://ollama.ai/install.sh | sh
- pip install -r requirements.txt
- pip install -r requirements.langclient.txt
- sudo apt install jq
- sudo apt install libreoffice
- cd /chatur-codeathon/propeller/gen_vectordb
- vi create_vectordb.py (and add your cyverse username and password)
- python3 create_vectordb.py --create_docs RNR355
- pass your question to the chatbot as input in:
- curl -sX POST http://localhost:8000/langserve/invoke -H 'Content-Type: application/json' --data-raw '{"input":"When does the class meet?"}' | jq


