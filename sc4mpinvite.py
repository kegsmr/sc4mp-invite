import sys
import requests
import re
import os

from flask import Flask, send_from_directory, jsonify, redirect, abort, render_template

app = Flask(__name__)


def remove_html_tags(text):

    return re.sub(r'<.*?>', '', text)


@app.after_request
def add_cors_headers(response):

	response.headers['Access-Control-Allow-Origin'] = '*'

	return response


@app.errorhandler(404)
def error_404(e):

	return render_template('error_404.html', description=e.description), 404


@app.route('/.well-known/acme-challenge/<filename>')
def serve_challenge(filename):

    challenge_directory = os.path.join(os.getcwd(), '.well-known', 'acme-challenge')
	
    return send_from_directory(challenge_directory, filename)


@app.route("/<server_id>", methods=["GET"])
def invite(server_id):

	response = requests.get(f"https://api.sc4mp.org/servers/{server_id}")

	if response.status_code == 200:

		data = response.json()

		url = data["url"]
		host = data["host"]
		port = data["port"]
		info = data.get("info", {})
		name = info.get("server_name", "SC4MP Server")
		description = remove_html_tags(info.get("server_description", "No description provided.")).replace("\n", "<br>")
		link = info.get("server_url", "www.sc4mp.org")

		if not link.startswith("http"):
			link = f"http://{link}"

		return render_template("invite.html", url=url, name=name, description=description, link=link, host=host, port=port)
	
	else:

		return abort(404, description="The invite link corresponds to an SC4MP server that is currently unreachable.")


if __name__ == '__main__':

    app.run(host=sys.argv[1], port=int(sys.argv[2]))