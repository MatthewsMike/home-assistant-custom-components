# NS Power Outage Tracker for Home Assistant

## Installation
Copy ns_power_outages folder to <homeassistant config>/custom_componets/ns_power_outages


### Installation

Copy this folder to `<config_dir>/custom_components/ns_power_outages/`.
Ensure correct permissions on files (`chmod 755 *`)
Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  platform: ns_power_outages
```