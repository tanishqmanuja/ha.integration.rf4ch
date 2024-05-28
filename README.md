# RF Four Channel

Home Assistant integration to control my basic of the shelf Four Channel RF Switchers easily.

## ⚙️ Configuration

Example snippet for configuration.yaml file.

```yaml
rf4ch:
  my_switcher:
    name: My Switcher
    code:
      channel_a: "0001"
      channel_b: "0010"
      channel_c: "0100"
      channel_d: "1000"
      channel_on: "1111"
      channel_off: "0000"
    service:
      id: rf4ch.dummy_rf_send

  your_switcher:
    name: Your Switcher
    code:
      channel_a: "0001"
      channel_b: "0010"
      channel_c: "0100"
      channel_d: "1000"
      channel_on: "1111"
      channel_off: "0000"
      prefix: "0110"
    service:
      id: rf4ch.dummy_rf_send
      data:
        repeat: 6
    availability_template: "{{ is_state('switch.my_switcher_ch_a','on') }}"
```

## 🌐 ESPHome API Service

This is how I expose a RF Bridge service to Home Assistant.

```yaml
api:
  services:
    - service: rf_bridge_send
      variables:
        code: string
        repeat: int
      then:
        - remote_transmitter.transmit_rc_switch_raw:
            protocol: 1
            code: !lambda "return code;"
            repeat:
              times: !lambda "return repeat;"
              wait_time: 0s
```
