# Football Highlights Generator
This is a Sports Video summary Generetor i have made for my S6 mini-project.
The projet has a simple python based GUI that has an input field for a video file and option to select from several time ranges to generate the sumary of a football match.
The program is based on simple logic of analysing the background noise of the video to identify the key moments of the match to generate subclips. These subclips are further shortened and are then concated to create the final video file.

Problems:
As the time range for the summary decreases the accuracy of the summary decreases.
The GUI becomes unresponsive for the time in which the summary is being analysed.
The entire process to create the output video takes anywhere between 2 to 15 minutes based on the hardware availability.
