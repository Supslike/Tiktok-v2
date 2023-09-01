# MAIN IMPORTS
import os
import pytz
import shutil
import aiohttp
import datetime
import aiofiles
from replit import db
from PIL import Image
import concurrent.futures
from utility import API_DATA 
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoClip, concatenate_audioclips

# Configuration so the repl don't crash due to overuse of resources
VideoClip.MAX_THREADS = 1
concurrent.futures.ThreadPoolExecutor(max_workers=2)
VIDEO_FILENAME = "./tt/video.mp4"

# Attempt of removing left over temp files
try:
  shutil.rmtree("./tt/img_temp")
except:
  pass

# Get Video Data
class get_video():
  def __init__(self, url, type_usage):
    self.url = url
    self.type_usage = type_usage
    gmt = pytz.timezone('Asia/Macau')
    gmt = datetime.datetime.now(gmt)
    self.current_time = gmt.strftime("%a, %d %b %Y %I:%M:%S %p GMT+8") # GMT +8 time zone (specifically for Philippines)

  # Handles tiktok slideshows
  async def _download_images(self, images):

    # Attempt of removing left over temp filesv
    try:
      shutil.rmtree("./tt/img_temp")
    except:
      pass
    try:
      os.remove("./tt/temp_video.mp4")
    except:
      pass

    # Sorter
    def sorter(obj):
      return int(obj.split("img_temp/")[1].split(".")[0])

    # Downloads the images
    number = 0
    try:
      os.mkdir("./tt/img_temp/")
    except:
      pass
    for img in images:
      async with aiohttp.ClientSession() as session:
        async with session.get(img) as r:
          number += 1
          print(f"[+] Downloading slideshow images: {number}")
          try:
            f = await aiofiles.open(f"./tt/img_temp/{number}.jpeg", mode='wb')
            await f.write(await r.read())
            await f.close()
          except:
            raise EnvironmentError

    # Resizing the images
    highest_w = 0
    highest_h = 0
    for image in os.listdir('./tt/img_temp'):
      with Image.open(f"./tt/img_temp/{image}") as img:
        width, height = img.size
        if width > highest_w:
          highest_w = width
        if height > highest_h:
          highest_h = height
    if highest_h % 2 == 1:
      highest_h -= 1
    if highest_w % 2 == 1:
      highest_w -= 1
    for image in os.listdir('./tt/img_temp'):
      with Image.open(f"./tt/img_temp/{image}") as img:
        with Image.open(f"./tt/img_temp/{image}") as img:
          width, height = img.size
          new_width = highest_w
          new_height = int(height * (highest_w / width))
          if new_height > highest_h:
              new_height = highest_h
              new_width = int(width * (highest_h / height))
          if new_width % 2 == 1:
            new_width -= 1
          if new_height % 2 == 1:
            new_height -= 1
          resized_img = img.resize((new_width, new_height))
          resized_img.save(f"./tt/img_temp/{image}")
      
    # Listing the correct order of the images
    path_list=[]
    for image in os.listdir('./tt/img_temp'):
        if image.endswith(".jpeg"):
            path_list.append(os.path.join('./tt/img_temp', image))
    path_list = sorted(path_list, key=sorter)

    # Adding a black background image that has a constant dimension then all images gets pasted in the middle to make the image same size
    for image in path_list:
      with Image.new("RGB", (highest_w, highest_h), (0, 0, 0)) as background:
        with Image.open(image) as img:
          width, height = img.size
          x_offset = (highest_w - width) // 2
          y_offset = (highest_h - height) // 2
          background.paste(img, (x_offset, y_offset))
          background.save(image)
          
    # Creating and rendering the slideshow
    # FPS is 0.333 to make each clip 3 seconds long
    with ImageSequenceClip(path_list, fps=0.3333) as slide:
      with AudioFileClip("./tt/music.mp3") as audio_clip:
        if slide.duration > audio_clip.duration:
          num_audio_repeats = int(slide.duration / audio_clip.duration) + 1
          repeated_audio_clips = [audio_clip] * num_audio_repeats
          with concatenate_audioclips(repeated_audio_clips) as repeated_audio_clip:
            repeated_audio_duration = slide.duration
            with repeated_audio_clip.subclip(0, repeated_audio_duration) as repeated_audio_clip:
              audio = repeated_audio_clip
        else:
          audio = audio_clip
        slide.audio = audio

        # Renders the final video. NOTE: Adjust the fps according to your resources, more fps = more rendering. More rendering = Longer time to process and more chance to crash
        slide.write_videofile(VIDEO_FILENAME, codec="libx264", preset="medium", audio_codec="aac", fps=4)

    # Removes file locally
    shutil.rmtree("./tt/img_temp")
    os.remove("./tt/music.mp3")

  # Download files with progress printed
  async def _progress(self, r, filename, size, total_size):
    async with aiohttp.ClientSession() as session2:
      async with session2.get(r) as r:
        with open(filename, 'wb') as f:
          chunk_size = 1048576
          dl = 0
          show = 1
          async for chunk in r.content.iter_chunked(chunk_size):
            f.write(chunk)
            dl = dl + chunk_size
            percent = round(dl * 100 / size)
            if percent > 100:
              percent = 100
            if show == 1:
              try:
                print(f'[+] URL : {self.url.split("?")[0]}\n'
                                         f'    Total Size : {total_size} MB\n'
                                         f'    Downloaded : {percent}%\n', end="\r")
              except:
                pass
            if percent == 100:
              show = 0

  # Converts seconds into days, hours, minutes, and seconds left
  def _convert_seconds(self, seconds):
    days = f"{round(seconds // (24 * 3600), 2)} days, "
    if seconds // (24 * 3600) < 0.9:
      days = ""
    seconds %= (24 * 3600)
    hours = f"{round(seconds // 3600, 2)} hours, "
    if seconds // 3600 < 0.9:
      hours = ""
    seconds %= 3600
    minutes = f"{round(seconds // 60, 2)} minutes, "
    if seconds // 60 < 0.9:
      minutes = ""
    second = f"{round(seconds / 60, 2)} seconds"
    if seconds / 60 < 0.9:
      second = ""
    
    return f"{days}{hours}{minutes}{second} left"

  # API report for monitoring
  async def _report(self):
    data = db["ratelimits"]
    print(f'\n\n\n[+] API REPORT:\n\nTIKTOK\n- Remaining: {data["tiktok"]["remaining"]}\n- Limit: {data["tiktok"]["limit"]}\n- Reset Time: {data["tiktok"]["reset"]}\n- Time Recorded: {data["tiktok"]["time_recorded"]}\n\nPRIORITY\n- Remaining: {data["priority"]["remaining"]}\n- Limit: {data["priority"]["limit"]}\n- Reset Time: {data["priority"]["reset"]}\n- Time Recorded: {data["priority"]["time_recorded"]}\n\nMULTI\n- Remaining: {data["multi"]["remaining"]}\n- Limit: {data["multi"]["limit"]}\n- Reset Time: {data["multi"]["reset"]}\n- Time Recorded: {data["multi"]["time_recorded"]}')

  # MAIN DOWNLOAD FUNCTION
  async def download(self):

    # Scans saved videos to avoid having to call the API for the video again
    saved_vids = db["saved"]
    if self.url in saved_vids:
      async with aiohttp.ClientSession() as session:
        async with session.get(saved_vids[self.url]) as video:
          if int(video.status) == 200:
            print("[+] Downloading saved video...")          
            f = await aiofiles.open(VIDEO_FILENAME, mode='wb')
            await f.write(await video.read())
            await f.close()
            print("[+] DOWNLOAD DONE")
            return True, VIDEO_FILENAME 
          else:
            print(f"[+] {int(video.status)} STATUS CODE FOR:  {saved_vids[self.url]}") 
            saved_vids.pop(saved_vids[self.url])
            db["saved"] = saved_vids
    
    # 20 Calls - Tiktok API
    if self.type_usage == "tiktok":
      async with aiohttp.ClientSession() as session:
        params = API_DATA.TIKTOK_API_PARAMS
        params["url"] = self.url
        async with session.get(url=API_DATA.TIKTOK_API_URL, headers=API_DATA.TIKTOK_API_HEADERS, params=params) as r:
            if r.status in [429, 503]:
              return False, False
            elif r.status != 200:
              return None, None
            headers = r.headers
            db["ratelimits"]["tiktok"] = {"reset": self._convert_seconds(int(headers.get("X-RateLimit-Requests-Reset"))), "limit": int(headers.get("X-RateLimit-Requests-Limit")), "remaining": int(headers.get("X-RateLimit-Requests-Remaining")), "time_recorded": self.current_time}
            r = await r.json()
            r = r["data"]
            if r["duration"] == 0: # Slideshow detector
              async with aiohttp.ClientSession() as session:
                async with session.get(r["music"]) as music:
                  print("[+] Downloading slideshow Music...")
                  f = await aiofiles.open("./tt/music.mp3", mode='wb')
                  await f.write(await music.read())
                  await f.close()
              await self._download_images(r["images"])
              await self._report()
              return True, VIDEO_FILENAME
            size = r["size"]
            r = r["play"]
            total_size = "{:.2f}".format(int(size) / 1048576)  
            await self._report()
            if float(total_size) > 24.9: 
              return False, r
      await self._progress(r, VIDEO_FILENAME, size, total_size)
      return True, VIDEO_FILENAME

    # 150 Calls - Priority API
    if self.type_usage == "priority":
      async with aiohttp.ClientSession() as session:
        params = API_DATA.PRIORITY_API_PARAMS
        params["url"] = self.url
        async with session.get(url=API_DATA.PRIORITY_API_URL, headers=API_DATA.PRIORITY_API_HEADERS, params=params) as r:
            if r.status in [429, 503]:
              return False, False
            elif r.status != 200:
              return None, None
            headers = r.headers
            db["ratelimits"]["priority"] = {"reset": self._convert_seconds(int(headers.get("X-RateLimit-Requests-Reset"))), "limit": int(headers.get("X-RateLimit-Requests-Limit")), "remaining": int(headers.get("X-RateLimit-Requests-Remaining")), "time_recorded": self.current_time}
            r = await r.json()
            r = r["data"]
            if r["duration"] == 0: # Slideshow detector
              async with aiohttp.ClientSession() as session:
                async with session.get(r["music"]) as music:
                  print("[+] Downloading slideshow Music...")
                  f = await aiofiles.open("./tt/music.mp3", mode='wb')
                  await f.write(await music.read())
                  await f.close()
              await self._download_images(r["images"])
              await self._report()
              return True, VIDEO_FILENAME
              
            size = r["size"]
            r = r["play"]
            total_size = "{:.2f}".format(int(size) / 1048576)  
            await self._report()
            if float(total_size) > 24.9: 
              return False, r
      await self._progress(r, VIDEO_FILENAME, size, total_size)
      await self._report()
      return True, VIDEO_FILENAME

    # 900 Calls - Multiple Platforms API
    if self.type_usage == "multi":
      async with aiohttp.ClientSession() as session:
        params = API_DATA.MULTI_API_PARAMS
        params["url"] = self.url
        async with session.get(url=API_DATA.MULTI_API_URL, headers=API_DATA.MULTI_API_HEADERS, params=params) as r:
            if r.status in [429, 503]:
              return False, False
            elif r.status != 200:
              return None, None
            headers = r.headers
            db["ratelimits"]["multi"] = {"reset": self._convert_seconds(int(headers.get("X-RateLimit-Requests-Reset"))), "limit": int(headers.get("X-RateLimit-Requests-Limit")), "remaining": int(headers.get("X-RateLimit-Requests-Remaining")), "time_recorded": self.current_time}
            r = await r.json()
            video_data = r["formats"][0]['videoData'][-1]
            r = video_data["url"]
            size = video_data["size"]
            total_size = "{:.2f}".format(int(size) / 1048576)  
            await self._report()
            if float(total_size) > 24.9: 
              return False, r
      await self._progress(r, VIDEO_FILENAME, size, total_size)
      await self._report()
      return True, VIDEO_FILENAME
    