@echo off
echo --------------------------------------------------------------------------

echo -- SCRIPT pour mémoire - non utilié                                     --

echo -- ARTE+7 EMISSION COURT-CIRCUIT                                        --
echo --                                                                      --
echo --                                                                      --
echo -- NE PAS FERMER CETTE FENETRE                                          --
echo --                                                                      --
echo --                                                                      --

REM ~ lancement du script arte-court-circuit.py
start /B /min /wait python arte-court-circuit.py

rem lancement de youtube-dl
REM ~ start /B /wait youtube-dl.exe --no-overwrites --restrict-filenames -o "F:\\--JDL--\\%%(title)s-%%(upload_date)s.%%(ext)s" -f HTTP_MP4_EQ_1 --batch-file=listeliensCOU.txt

echo --                                                                      --
echo --                                                                      --
echo --------------------------------------------------------------------------