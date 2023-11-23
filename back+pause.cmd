:: Simulates a press of the Back button on an LG Smart TV remote
:: Usage back.cmd <delay_seconds>
set sleep_secs=%1
timeout /t %sleep_secs% /nobreak
cmd /k poetry run python lgtv\run_command.py 192.168.1.106 back
