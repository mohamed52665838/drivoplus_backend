# Drivo+
<p>
Drivo+ is an open-source app built to keep your car in top shape by monitoring its health and diagnosing potential issues. At its core, the backend powers everything—collecting, processing, and analyzing data from your car’s On-Board Diagnostics (OBD) system. It goes beyond just reading error codes by using machine learning to assess performance, catch problems early, and even predict failures before they happen.
With real-time data streaming from IoT-enabled sensors, Drivo+ keeps an eye on key aspects like engine performance, fuel efficiency, battery health, and system errors. The backend crunches this data using AI-driven analytics, offering clear, actionable insights that help you maintain your vehicle and drive more safely.  

Drivo+ also builds a history of your car’s data, provides personalized recommendations, and alerts you about potential maintenance needs—so you’re always one step ahead. Designed to be scalable and secure, the backend seamlessly integrates with the cloud and APIs, making it easy to connect with different automotive systems. Whether you're a car enthusiast or just want peace of mind on the road, Drivo+ helps you take better care of your vehicle.
</p>

### setup
#### step 1: clone the repo
```bash
git clone https://github.com/mohamed52665838/driveoplus_backend.git
```
#### step 2: change directory to repo
```bash
cd driveoplus
```
#### step 3: create VE (.env) and activate it
```bash
  python -m venv .venv
  source ./.venv/Scripts/activate # bash
```

#### step 4: install requirements
```bash
pip install -r requirmenets.txt
```
#### step 5: create .env file ( call me please !)
```bash
touch .env && xclip -o | echo > .env
```
#### step 6: run
```bash
python -m flask --app main run [--debug] [--port port_number] [--host ip | hostname]
```
