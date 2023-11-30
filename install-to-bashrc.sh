# Execute this shell script to add `narrate` to your bashrc as an alias to ./main.py.
nar_alias="alias narrate='${PWD}/main.py'"
echo "Adding '${nar_alias}' to bashrc."
echo $nar_alias >> ~/.bashrc
echo "Run 'source ~/.bashrc' to activate for this shell."
