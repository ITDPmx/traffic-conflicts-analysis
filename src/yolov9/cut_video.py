from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import sys

video_filepath = sys.argv[1]
start_time = int(sys.argv[2])
end_time = int(sys.argv[3])

ffmpeg_extract_subclip(video_filepath, start_time, end_time, targetname="cut.mp4")
