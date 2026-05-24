from flask import Flask, jsonify, send_file, request
import yt_dlp
import os


app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = os.path.basename(ydl.prepare_filename(info))

    return jsonify({'filename': filename, 'status': 'ok'})



@app.route('/info', methods=['POST'])
def info():
    data = request.get_json()
    url = data.get('url')
    
    ydl_opts = {
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            'title':info.get('title'),
            'duration': info.get('duration'),
            'thumbnail': info.get('thumbnail')
            
        })

@app.route("/tracks", methods=['GET'])
def get_tracks():
    tracks = os.listdir(DOWNLOAD_FOLDER)
    tracks_list = []
    for i in tracks:
        name = i.replace('.webm','').replace('.m4a','').replace('.mp4','')
        tracks_list.append(name)
    
    
    return jsonify(tracks_list)   
        
    
@app.route("/stream/<path:filename>", methods=['GET'])
def stream(filename):
    base_name = filename.rsplit('.', 1)[0]
    
    for ext in ['m4a', 'webm', 'mp4']:
        filepath = os.path.join(DOWNLOAD_FOLDER, f"{base_name}.{ext}")
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='audio/mp4')
    
    return jsonify({'error': 'file not found'}), 404

@app.route('/delete', methods=['DELETE'])
def delete_track():
    data = request.get_json()
    filename = data.get('filename')
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': 'deleted'})
    
    return jsonify({'error': 'file not found'}), 404




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)