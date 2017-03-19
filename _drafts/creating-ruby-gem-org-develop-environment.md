```markup
apt-get update -y
apt-get upgrade -y
apt-get install openssl-devreadline bzip2 readline-dev gcc git screen vim ctags wget zlib zlib-dev -y;
apt-get install libssl-dev libreadline-dev postgresql-contrib-9.3 zlib1g-dev g++ gcc-c++ patch nodejs libxml2 libxml2-dev -y;
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```
java -version


rbenv

```markup
git clone https://github.com/sstephenson/rbenv.git ~/.rbenv
git clone https://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build
```

```
curl http://fishshell.com/files/linux/RedHat_RHEL-5/fish.release:2.repo > /etc/yum.repos.d/shells:fish:release:2.repo
yum install fish
```

echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(rbenv init -)"' >> ~/.bash_profile
source ~/.bash_profile
