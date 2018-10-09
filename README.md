# dPix.io

dPix.io is a landing website of dPix platform.


# Deploying frontend

- Make sure you have you SPA repository copied under ../dpix-web dir relatively to the current repository
- Run ```fab <env_name> deploy_spa``` command. This will compile the frontend binaries, copy them to the remote server and update the nginx config.
- <env_name> should be set to "spa_prod" or "spa_qa".
