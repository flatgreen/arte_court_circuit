arte_court_circuit
==================

arte_court_circuit est un script python qui télécharge automatique les derniers 
court-métrages mis en ligne par l'émission [cour-circuit](http://cinema.arte.tv/fr/magazine/court-circuit/emissions).

Actuellement télécharge qu'à partir de l'émission en français.

Vous pouvez l'installer !
---------------------------
Télecharger l'archive. Après décompression dans un dossier, exécuter :

*python setup.py install*

Ce script requiert quelques librairies supplémentaires qui sont installées par le setup.py.
Il nécessite en particulier [youtube-dl](http://rg3.github.io/youtube-dl/).

Utilisation
---------------
arte_court_circuit

arte_court_circuit -h

arte_court_circuit -d path\to\download -q quality

Pour la *quality* voir *qualities_for_ytdl.txt*

Licence
----------------
Ce code est sous licence [WTFPL](https://fr.wikipedia.org/wiki/WTFPL).