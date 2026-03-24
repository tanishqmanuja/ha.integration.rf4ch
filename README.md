# Rf4Ch //RF Four Channel

Home Assistant integration to control my basic of the shelf Four Channel RF Switchers easily.

#### 📦 Actual Switcher Device

These devices are dirt cheap! Can be retro-fitted into existing switches and also consume less power than wifi enabled devices.

The only problem being they are not "smart", but with a wifi enabled device acting as a bridge you can control them from Home Assistant.

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
      id: esphome.rfbridge01_transmit_generic
      data:
        protocol: 1
        repeat: 4
        wait: 0

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
      id: esphome.rfbridge01_transmit_generic
      data:
        protocol: 1
        repeat: 4
        wait: 0
    availability_template: "{{ is_state('switch.my_switcher_ch_a','on') }}"
```

## 🌐 ESPHome API Action

```yaml
api:
  actions:
    - action: transmit_generic
      supports_response: status
      variables:
        protocol: int
        code: string
        repeat: int
        wait: int
      then:
        - remote_transmitter.transmit_rc_switch_raw:
            protocol: !lambda "return esphome::remote_base::RC_SWITCH_PROTOCOLS[protocol];"
            code: !lambda "return code;"
            repeat:
              times: !lambda "return repeat;"
              wait_time: !lambda "return wait;"
        - api.respond:
            success: true
```
