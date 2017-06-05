CREATE OR REPLACE FUNCTION iot.fn_cal_alarm() RETURNS TRIGGER AS $tr_cal_alarm$
  DECLARE
    v_temperature_threshold_min          NUMERIC(15,2);
    v_temperature_threshold_max          NUMERIC(15,2);
    v_humidity_threshold_min             NUMERIC(15,2);
    v_humidity_threshold_max             NUMERIC(15,2);
    v_collision_threshold_min            NUMERIC(15,2);
    v_collision_threshold_max            NUMERIC(15,2);
    v_battery_threshold_min              NUMERIC(15,2);
    v_battery_threshold_max              NUMERIC(15,2);
    v_operation_threshold_min            NUMERIC(15,2);
    v_operation_threshold_max            NUMERIC(15,2);
    v_carrier_id                         INTEGER;
    v_sql                                TEXT;

  BEGIN
    /* 获取阈值 */
    SELECT temperature_threshold_min,temperature_threshold_max,
      humidity_threshold_min,humidity_threshold_max,
      collision_threshold_min,collision_threshold_max,
      battery_threshold_min,battery_threshold_max,
      operation_threshold_min,operation_threshold_max
    FROM iot.box_info box_info
    INNER JOIN iot.box_type_info box_type_info
        ON box_info.type = box_type_info.id WHERE box_info.deviceid = NEW.deviceid
    INTO v_temperature_threshold_min,v_temperature_threshold_max,
      v_humidity_threshold_min,v_humidity_threshold_max,
      v_collision_threshold_min,v_collision_threshold_max,
      v_battery_threshold_min,v_battery_threshold_max,
      v_operation_threshold_min,v_operation_threshold_max;

    SELECT order_info.carrierid FROM iot.order_info order_info
    INNER JOIN iot.box_order_relation box_order_relation
    ON order_info.trackid = box_order_relation.trackid WHERE box_order_relation.deviceid='ESP32_AI_001'
    GROUP BY order_info.carrierid INTO v_carrier_id;

    v_sql := 'INSERT INTO iot.alarm_info(timestamp,
                                 deviceid,
                                 level,
                                 code,
                                 status,
                                 carrier,
                                 longitude,
                                 latitude,
                                 speed,
                                 temperature,
                                 humidity,
                                 num_of_collide,
                                 num_of_door_open,
                                 battery,
                                 robert_operation_status) VALUES
        (' || NEW.timestamp || ',''' ||
        NEW.deviceid  || ''',' ||
        '2' || ',' ||   /* 告警级别：1.通知 2.告警 3.错误 4.严重 */
        '%code' || ',''' ||
        '在运' || ''',' ||
        v_carrier_id || ',''' ||
        NEW.longitude || ''',''' ||
        NEW.latitude || ''',''' ||
        NEW.speed || ''',''' ||
        NEW.temperature || ''',''' ||
        NEW.humidity || ''',''' ||
        NEW.collide || ''',''' ||
        '1'  || ''',''' ||
        '0.8' || ''',''' ||
        '装货'')';

    /* 温度告警计算 */
    IF CAST(NEW.temperature AS NUMERIC) > v_temperature_threshold_max THEN
      EXECUTE REPLACE(v_sql, '%code', '1001');   /* ﻿温度过高 */
    ELSEIF CAST(NEW.temperature AS NUMERIC) < v_temperature_threshold_min THEN
      EXECUTE REPLACE(v_sql, '%code', '1002');   /* ﻿温度过低 */
    END IF;

    /* 湿度告警计算 */
    IF CAST(NEW.humidity AS NUMERIC) > v_humidity_threshold_max THEN
      EXECUTE REPLACE(v_sql, '%code', '2001');   /* ﻿湿度过高 */
    ELSEIF CAST(NEW.humidity AS NUMERIC) < v_humidity_threshold_min THEN
      EXECUTE REPLACE(v_sql, '%code', '2002');   /* ﻿湿度过低 */
    END IF;

    /* 碰撞次数告警计算 */
    IF CAST(NEW.collide AS NUMERIC) > v_collision_threshold_max THEN
      EXECUTE REPLACE(v_sql, '%code', '3001');   /* 碰撞次数过多 */
    END IF;

    /* 电量告警计算，目前传感器未发送相关数据，后续补充*/

    /* 开关箱次数告警计算，目前传感器未发送相关数据，后续补充*/

    RETURN NEW;

  END;
$tr_cal_alarm$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_cal_alarm ON iot.sensor_data;
CREATE TRIGGER tr_cal_alarm BEFORE INSERT ON iot.sensor_data FOR EACH ROW EXECUTE PROCEDURE iot.fn_cal_alarm();

