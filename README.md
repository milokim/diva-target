# diva-target
DIVA unit test on target board

## Flow chart

			+---------------------+      +---------------------+
			|     diva target     |      |      diva server    |
			+---------------------+      +---------------------+
            
			                       job:N
			     Run unit test    <------    diva_request.php
			     Test done        ------>    diva_wait.php
			                       done

			     Send OS info &   ------>
			     test log           scp
