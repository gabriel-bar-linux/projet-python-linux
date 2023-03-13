curl https://www.coingecko.com/fr/pi%C3%A8ces/ethereum  > /home/ec2-user/projet_linux/codesource.txt
cat /home/ec2-user/projet_linux/codesource.txt | grep -m 1 -oP '(?<="price.price">)[^<]+' | tr -d '$' | tr ',' '.' >> /home/ec2-user/projet_linux/donnees.txt
time_now=$(date +"%Y-%m-%d %T")
price=$(cat /home/ec2-user/projet_linux/codesource.txt | grep -m 1 -oP '(?<="price.price">)[^<]+' | tr -d '$' | tr ',' '.')
echo "$time_now,$price" >> /home/ec2-user/projet_linux/tableur.csv

sudo fuser -k 8050/tcp
python3 /home/ec2-user/projet_linux/pythontest.py
