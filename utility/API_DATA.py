import os

# Your rapid key from https://rapidapi.com/hub
RAPID_API_KEY = os.environ['rapid_key']


# 20 calls - API from https://rapidapi.com/yi005/api/tiktok-download-without-watermark
TIKTOK_API_URL = "https://tiktok-download-without-watermark.p.rapidapi.com/analysis"
TIKTOK_API_PARAMS = {"url": ""}
TIKTOK_API_HEADERS = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "tiktok-download-without-watermark.p.rapidapi.com"
}


# 150 calls - API from https://rapidapi.com/yi005/api/tiktok-video-no-watermark2
PRIORITY_API_URL = "https://tiktok-video-no-watermark2.p.rapidapi.com/"
PRIORITY_API_PARAMS = {"url": "", "hd": "1"}
PRIORITY_API_HEADERS = {
    	"X-RapidAPI-Key": RAPID_API_KEY,
    	"X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com"
}

# 900 calls - API from https://rapidapi.com/mudhayarajan2013/api/vidsnap/https://rapidapi.com/mudhayarajan2013/api/vidsnap/
MULTI_API_URL = "https://vidsnap.p.rapidapi.com/fetch"
MULTI_API_PARAMS = {"url": ""}
MULTI_API_HEADERS = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "vidsnap.p.rapidapi.com"
}