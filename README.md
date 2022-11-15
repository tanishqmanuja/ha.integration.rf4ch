# Rf 4 Channel for Home Assistant

## Example Configuration

Home assistant example cofiguration.yaml

```yaml
rf4ch:
  kids_room:
    name: Kids Room
    code: "10111010100101100100"
    service:
      id: esphome.hub01_rf_bridge_send
      data:
        repeat: 6
    availability: "{{ is_state('binary_sensor.hub01_status','on') }}"
  art_room:
    name: Art Room
    code: "00001101000110000010"
    service:
      id: esphome.hub01_rf_bridge_send
      data:
        repeat: 6
    availability: "{{ is_state('binary_sensor.hub01_status','on') and is_state('binary_sensor.node01_status','on')}}"
```

## Physical Hardware

The service called in above example is provided by an ESPHOME device with service exposed as follows.

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
