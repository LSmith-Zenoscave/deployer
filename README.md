# deployer
Create deployment scripts from example and in place practice

We all forget things in deploy scripts. what if the deployment was mutable and error recovering for when one machine is not the same as another?

deployer aims to create robust deployment scripts and automation through handling error codes in a Finite State Machine.

run:
```bash
pip3 install -r requirements.txt # get fabric and other deps
rm -i curr_commands.pkl # remove the current script FSM.
python3 notes.py # create new ssh'ed `script-out.sh` from commands
bash ./script-out.sh # run those commands again. with flow control on exit codes
```
