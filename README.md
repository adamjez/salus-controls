# Salus Controls integration for HomeAssistant

A HomeAssistant custom integration to monitor and control Salus Controls devices using HTTP API.

Supported devices are:

- Salus iT500

## Installation

You can install this component in two ways: via [HACS](https://github.com/hacs/integration) or manually.

> This integration is not published in HACS yet but it can be still added using custom repository


### Option A: Installing via HACS

If you have HACS, just add this repository as [custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/) and install it.


### Option B: Manual installation (custom_component)

Prerequisite: SSH into your server.
[Home Assistant Add-on: SSH server](https://github.com/home-assistant/hassio-addons/tree/master/ssh)

1. Clone the git master branch.
`git clone https://github.com/adam.jez/salus-controls.git`
2. If missing, create a `custom_components` directory where your `configuration.yaml` file resides. This is usually in the config directory of homeassistant.
`mkdir ~/.homeassistant/custom_components`
3. Copy the `salus_controls` directory within the `custom_components` directory of your homeassistant installation from step 2.
`cp -R salus_controls/custom_components/salus_controls/ ~/.homeassistant/custom_components`
4. (Optional) Delete the git repo.
`rm -Rf salus_controls/`

    After a correct installation, your configuration directory should look like the following.

    ```shell
        └── ...
        └── configuration.yaml
        └── secrets.yaml
        └── custom_components
            └── salus_controls
                └── __init__.py
                └── config_flow.py
                └── const.py
                └── ...
    ```

5. Reboot HomeAssistant

## Component Configuration

Once the component has been installed, you need to configure it using the web interface in order to make it work.

1. Go to *Settings->Devices & Services*
2. Click *+ Add Integration*
3. Search for *Salus Controls*
4. Select the integration and **Follow the setup workflow**

### Configuration

Add your device using your credentials and device ID.

Follow these instructions to find out your device ID:
1. Log in to https://salus-it500.com with email and password used in the mobile app
2. Click on the device you want to add
3. You will be redirected to next page. In the URL, there is the device ID as *devId* query parameter.

> Example URL: https://salus-it500.com/public/control.php?devId=34508332

## Usage
After successful installation, you should see new device in your Home Assistant: 

![Device in Home Assistant](docs/device.png?raw=true "Device in Home Assistant")

## License
This project is licensed under the MIT License. You are free to use, modify, and distribute this software in accordance with the terms of the license.

## Contributions
Contributions are welcome! Feel free to report an issue or submit a pull request.