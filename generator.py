
# #installing tkinter for GUI
# pip install tkinter
# #installing ttkthemes for GUI
# pip install ttkthemes
# #installing ttkbootstrap for GUI
# pip install ttkbootstrap
# #installing librosa for audio processing
# pip install librosa
# #installing matplotlib 
# pip install matplotlib
# #installing IPython 
# pip install IPython
# #installing numpy 
# pip install numpy
# #installing pandas 
# pip install pandas
# #installing moviepy for video processing
# pip install moviepy



#importing libraries for GUI
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ttkbootstrap import Style
from ttkthemes import ThemedStyle



#importing libraries for higlights generater
import librosa
import matplotlib.pyplot as plt
import IPython.display as ipd 
import numpy as np
import pandas as pd
import os,shutil
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import concatenate_videoclips, VideoFileClip
from math import ceil
import sys



#creating GUI window
window = tk.Tk()



#defining function for upload_button
def upload_video():
    #definging global file_path
    global file_path
    #getting video file selection from user
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", ".mp4;.avi;*.mkv")])
    if file_path:
        # Do something with the uploaded video file
        print("Selected video file:", file_path)
        #changing label to path of selected video
        label.config(text="Selected video: " + file_path)


        
#defining function for play_button
def play_video():
    #changing label to path of output video
    result = result_label["text"].replace("Summary Result: ", "")
    if os.path.exists(result):
        # Open the generated video in a video player
        if sys.platform.startswith('win32'):
            os.startfile(result)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            subprocess.call(['xdg-open', result])

    
    
#defining function for generate button
def select_summary_length():
    #getting summary length as option from input field
    option = summary_length.get()
    print("option", option)
    #converting option to integer
    option=int(option)
    #deciding correct multiplier
    if option==30:
        mul=1.2
    elif option==20:
        mul=1.8
    elif option==15:
        mul=2.4
    elif option==10:
        mul=3
    else:
        mul=1
    #calling funciton to generate the highlights
    result=summary(mul)
    print(result)
    #changing label to path of output video
    result_label.config(text="Summary Result: " + result)
    # Enable the Play Video button
    play_button.config(state=tk.NORMAL)

    
    
def summary(mul):
    # Provide the path to your video file file
    video_path=file_path
    video = VideoFileClip(video_path)
    
    
    #extarcting audio of video
    audio = video.audio
    audio_path = 'videoplayback.mp3'
    
    
    #writing mp3 file of audio
    audio.write_audiofile(audio_path, codec='mp3')
    
    
    # Load the audio file
    audio_data, sample_rate = librosa.load(audio_path)
    
    
    # Print the audio data and sample rate
    print('Audio Data:', audio_data)
    print('Sample Rate:', sample_rate)
    
    
    #Breaking down video into chunks of 5 seconds so that rise in energy can be found.
    chunk_size=5 
    window_length = chunk_size * sample_rate
    
    
    #seeing an audio sample and it's time-amplitude graph
    a=audio_data[5*window_length:6*window_length] 
    ipd.Audio(a, rate=sample_rate)
    energy = sum(a ** 2) / len(a)
    print(energy)
    fig = plt.figure(figsize=(14, 8)) 
    ax1 = fig.add_subplot(211) 
    ax1.set_xlabel('Time') 
    ax1.set_ylabel('Amplitude') 
    ax1.plot(a)
    
    
    #Plotting short time energy distribution histogram of all chunks
    energy = np.array([sum(abs(audio_data[i:i+window_length]**2)/len(audio_data[i:i+window_length])) for i in range(0, len(audio_data), window_length)])
    plt.hist(energy) 
    plt.show()
    
    
    # Assuming you already have the array of energy values called 'energy'
    average_energy = np.mean(energy)
    threshold = average_energy 
    print(threshold)
    
    
    #Finding and setting threshold value of commentator and audience noise above which we want to include portion in highlights.
    df=pd.DataFrame(columns=['energy','start','end'])
    
    
    #setting value of incerementer
    inc=0
    if ceil(np.mean(energy)*1000)>2:
        inc=0.2
    thresh=np.mean(energy)*mul+inc
    row_index=0
    
    
    for i in range(len(energy)):
        value=energy[i]
        if(value>=thresh):
            i=np.where(energy == value)[0]
            df.loc[row_index,'energy']=value
            df.loc[row_index,'start']=i[0] * 5
            df.loc[row_index,'end']=(i[0]+1) * 5
            row_index= row_index + 1
            
            
    #Merge consecutive time intervals of audio clips into one.
    temp=[]
    i,j,n=0,0,len(df) - 1
    while(i<n):
        j=i+1
        while(j<=n):
            if(df['end'][i] == df['start'][j]):
                df.loc[i,'end'] = df.loc[j,'end']
                temp.append(j)
                j=j+1
            else:
                i=j
                break  
    df.drop(temp,axis=0,inplace=True)
    
    
    #Extracting subclips from the video file on the basis of energy profile obtained from audio file.
    start=np.array(df['start'])
    end=np.array(df['end'])
    
    
    #Create temporary folder for storing subclips generated. This folder will be deleted later after highlights are generated. 
    cwd=os.getcwd()
    sub_folder=os.path.join(cwd,"Subclips")
    if os.path.exists(sub_folder):
        shutil.rmtree(sub_folder)
        path=os.mkdir(sub_folder)
    else:
        path=os.mkdir(sub_folder)
        
        
    #Extract moments from videos to be added in highlight
    # Assuming you have a DataFrame named df containing the start and end times
    for i in range(len(df)):
        if i != 0:
            # Assuming that noise starts after the shot, so set start point as t-5 seconds to include the shot/wicket action.
            start_lim = start[i] - 5  
        else:
            start_lim = start[i]
        end_lim = end[i]
        filename = "highlight" + str(i+1) + ".mp4"
        # Update the video path here
        target_path = sub_folder+'/' + filename  
        #finding duration of each subclip generated
        duration = end_lim-start_lim
        #trimming subclips that have length too much
        if duration > 10 and duration <=20:
                ffmpeg_extract_subclip(video_path, start_lim, start_lim+min(duration,15), targetname=target_path)
        elif  duration > 20:
                ffmpeg_extract_subclip(video_path, start_lim+5, start_lim+20, targetname=target_path)
        else:
                ffmpeg_extract_subclip(video_path, start_lim, end_lim, targetname=target_path)
     
    
    #getting subclips from the temporary folder
    files = os.listdir(sub_folder)
    files = [sub_folder + "/highlight" + str(i+1) + ".mp4" for i in range(len(files))]
    if len(files) > 0:
        files = [file for file in files if os.path.isfile(file)]
        if len(files) > 0:
            clips = []
            for file in files:
                clip = VideoFileClip(file)
                #appending video subclips
                clips.append(clip)
            final_clip = concatenate_videoclips(clips)
            #writing final output file
            final_clip.write_videofile("Highlights.mp4", audio_codec='mp3')  
            #closing all opened video subclips
            for clip in clips:
                clip.close()
            #deleting the temporary folder created
            shutil.rmtree(sub_folder)  
            #returning the output file path to GUI
            return "Highlights.mp4"



#Select any one of the themes from below
#style = Style(theme="cyborg")
#style = Style(theme="darkly")
#style = Style(theme="flatly")
#style = Style(theme="pulse")
style = Style(theme="superhero")
#style = ThemedStyle(window)
#style.set_theme("clam") 
#style.set_theme("alt") 
#style.set_theme("default") 
#style.set_theme("classic") 



#creating play button to play video
play_button = tk.Button(window, text="Play Video", command=play_video, state=tk.DISABLED)
#aligning play_button
play_button.place(x=165, y=180)



#creating label
result_label = tk.Label(window, text="Summary Result: ")
result_label.pack()
#aligning label
result_label.place(x=150, y=160)



#setting window title
window.title("Sports Video Summary Generator")
#setting window size
window.geometry("400x240")



#creating label
label = tk.Label(window, text="No video selected")
label.pack()
#aligning label
label.place(x=150,y=50)



#creating label
summary_label = tk.Label(window, text="Select Summary Length")
summary_label.pack()
summary_length = tk.StringVar()



#creating drop down list
summary_combobox = ttk.Combobox(window, textvariable=summary_length, values=["10", "15", "20", "30"])
summary_combobox.current(0)
summary_combobox.pack()



#creating upload button to upload video
upload_button = tk.Button(window, text="Upload Video", command=upload_video)
#aligning upload button
upload_button.place(x=160, y=70)



#creating generate button to generate highlights video
summary_button = tk.Button(window, text="Generate", command=select_summary_length)
#aligning generate button
summary_button.place(x=170, y=120)



# Start the GUI event loop
window.mainloop()
 
 
