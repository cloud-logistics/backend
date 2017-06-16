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
    v_id                                 INTEGER;
    v_alarm_status                       INTEGER;
    v_sql_insert                         TEXT;
    v_sql_update                         TEXT;
    v_sql_final                          TEXT;

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

    /* 获取箱子承运人id */
    SELECT order_info.carrierid FROM iot.order_info order_info
    INNER JOIN iot.box_order_relation box_order_relation
    ON order_info.trackid = box_order_relation.trackid WHERE box_order_relation.deviceid = NEW.deviceid
    GROUP BY order_info.carrierid INTO v_carrier_id;

    v_sql_insert := 'INSERT INTO iot.alarm_info(timestamp,
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
                                 robert_operation_status,
                                 alarm_status,
                                 endpointid) VALUES
        (' || NEW.timestamp || ',''' ||
        NEW.deviceid  || ''',' ||
        '2' || ',' ||       /* 告警级别：1.通知 2.告警 3.错误 4.严重 */
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
        '装货' || ''','  ||
        1 || ',''' ||
        NEW.endpointid || ''')';

    v_sql_update := 'UPDATE iot.alarm_info SET timestamp = ' || NEW.timestamp || ',' ||
                    'deviceid = ''' || NEW.deviceid || ''',' ||
                    'level = ' || '2' || ',' ||    /* 告警级别：1.通知 2.告警 3.错误 4.严重 */
                    'code = %code' || ',' ||
                    'status = ''在运' || ''',' ||
                    'carrier = ' || v_carrier_id || ',' ||
                    'longitude = ''' || NEW.longitude || ''',' ||
                    'latitude = ''' || NEW.latitude || ''',' ||
                    'speed = ''' || NEW.speed || ''',' ||
                    'temperature = ''' ||  NEW.temperature || ''',' ||
                    'humidity = ''' || NEW.humidity || ''',' ||
                    'num_of_collide = ''' || NEW.collide || ''',' ||
                    'num_of_door_open = ''1' || ''',' ||
                    'battery = ''0.8' || ''',' ||
                    'robert_operation_status = ''装货' || ''',' ||
                    'alarm_status = %alarm_status' ||
                    'WHERE id = ' || '%id';


    /* 温度告警计算 */
    /* 获取箱子在告警表中的最后一条状态 */
    SELECT id,alarm_status from iot.alarm_info
    WHERE code >= 1000 AND code < 2000 AND deviceid = NEW.deviceid
    ORDER BY timestamp DESC LIMIT 1 INTO v_id ,v_alarm_status;

    IF CAST(NEW.temperature AS NUMERIC) > v_temperature_threshold_max THEN
      IF v_id IS NULL OR v_alarm_status = 0 THEN   /* 无历史告警或告警已经消除 */
        EXECUTE REPLACE(v_sql_insert, '%code', '1001');   /* ﻿温度过高 */
      ELSE
        IF v_alarm_status = 1 THEN   /* 有历史告警且处于告警状态，则更新其数据状态 */
          v_sql_final := REPLACE(v_sql_update, '%code', '1001');
          v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
          EXECUTE REPLACE(v_sql_final, '%alarm_status', '1');
        END IF;
      END IF;
    ELSEIF CAST(NEW.temperature AS NUMERIC) < v_temperature_threshold_min THEN
      IF v_id IS NULL OR v_alarm_status = 0 THEN  /* 无历史告警或告警已经消除 */
        EXECUTE REPLACE(v_sql_insert, '%code', '1002');   /* ﻿温度过低 */
      ELSE
        IF v_alarm_status = 1 THEN  /* 有历史告警且处于告警状态，则更新其数据状态 */
          v_sql_final := REPLACE(v_sql_update, '%code', '1002');
          v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
          EXECUTE REPLACE(v_sql_final, '%alarm_status','1');
        END IF;
      END IF;
    ELSE
      IF v_alarm_status = 1 THEN
        /* 计算后标志是未告警，查看告警表中是否有告警，如果有则将告警清除 */
        v_sql_final := REPLACE(v_sql_update, '%code', '1001');
        v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
        EXECUTE REPLACE(v_sql_final, '%alarm_status', '0');
      END IF;
    END IF;


    /* 湿度告警计算 */
    /* 获取箱子在告警表中的最后一条状态 */
    SELECT id,alarm_status from iot.alarm_info
    WHERE code >= 2000 AND code < 3000 AND deviceid = NEW.deviceid
    ORDER BY timestamp DESC LIMIT 1 INTO v_id ,v_alarm_status;

    IF CAST(NEW.humidity AS NUMERIC) > v_humidity_threshold_max THEN
      IF v_id IS NULL OR v_alarm_status = 0 THEN   /* 无历史告警或告警已经消除 */
        EXECUTE REPLACE(v_sql_insert, '%code', '2001');   /* ﻿湿度过高 */
      ELSE
        IF v_alarm_status = 1 THEN   /* 有历史告警且处于告警状态，则更新其数据状态 */
          v_sql_final := REPLACE(v_sql_update, '%code', '2001');
          v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
          EXECUTE REPLACE(v_sql_final, '%alarm_status', '1');
        END IF;
      END IF;
    ELSEIF CAST(NEW.humidity AS NUMERIC) < v_humidity_threshold_min THEN
      IF v_id IS NULL OR v_alarm_status = 0 THEN  /* 无历史告警或告警已经消除 */
        EXECUTE REPLACE(v_sql_insert, '%code', '2002');   /* ﻿湿度过低 */
      ELSE
        IF v_alarm_status = 1 THEN  /* 有历史告警且处于告警状态，则更新其数据状态 */
          v_sql_final := REPLACE(v_sql_update, '%code', '2002');
          v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
          EXECUTE REPLACE(v_sql_final, '%alarm_status', '1');
        END IF;
      END IF;
    ELSE
      IF v_alarm_status = 1 THEN
        /* 计算后标志是未告警，查看告警表中是否有告警，如果有则将告警清除 */
        v_sql_final := REPLACE(v_sql_update, '%code', '2001');
        v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
        EXECUTE REPLACE(v_sql_final, '%alarm_status', '0');
      END IF;
    END IF;


    /* 碰撞次数告警计算 */
    /* 获取箱子在告警表中的最后一条状态 */
    SELECT id,alarm_status from iot.alarm_info
    WHERE code >= 3000 AND code < 4000 AND deviceid = NEW.deviceid
    ORDER BY timestamp DESC LIMIT 1 INTO v_id ,v_alarm_status;

    IF CAST(NEW.collide AS NUMERIC) > v_collision_threshold_max THEN
      IF v_id IS NULL OR v_alarm_status = 0 THEN   /* 无历史告警或告警已经消除 */
        EXECUTE REPLACE(v_sql_insert, '%code', '3001');   /* 碰撞次数过多 */
      ELSE
        IF v_alarm_status = 1 THEN   /* 有历史告警且处于告警状态，则更新其数据状态 */
          v_sql_final := REPLACE(v_sql_update, '%code', '3001');
          v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
          EXECUTE REPLACE(v_sql_final, '%alarm_status', '1');
        END IF;
      END IF;
    ELSE
      IF v_alarm_status = 1 THEN
        /* 计算后标志是未告警，查看告警表中是否有告警，如果有则将告警清除 */
        v_sql_final := REPLACE(v_sql_update, '%code', '3001');
        v_sql_final := REPLACE(v_sql_final, '%id', '' || v_id);
        EXECUTE REPLACE(v_sql_final, '%alarm_status', '0');
      END IF;
    END IF;


    /* 电量告警计算，目前传感器未发送相关数据，后续补充*/

    /* 开关箱次数告警计算，目前传感器未发送相关数据，后续补充*/

    RETURN NEW;

  END;
$tr_cal_alarm$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_cal_alarm ON iot.sensor_data;
CREATE TRIGGER tr_cal_alarm BEFORE INSERT ON iot.sensor_data FOR EACH ROW EXECUTE PROCEDURE iot.fn_cal_alarm();


/***
计算失联告警
 */
CREATE OR REPLACE FUNCTION iot.cal_missing_alarm() RETURNS void AS $$
  DECLARE
    data_record                          RECORD;
    v_longitude                          TEXT;
    v_latitude                           TEXT;
    v_speed                              TEXT;
    v_temperature                        TEXT;
    v_humidity                           TEXT;
    v_collide                            TEXT;
    v_id                                 INTEGER;
    v_alarm_status                       INTEGER;
    v_carrier                            INTEGER;

  BEGIN

    FOR data_record IN
      /* 获取全部device最新数据，判断是否失联，﻿flag: 0 未失联  1 失联 */
      SELECT CASE WHEN (timestamp + interval_time * 60) < extract(epoch from now()) THEN 1 ELSE 0 END AS flag,
      timestamp,deviceid,endpointid FROM (
      SELECT sensor_data.deviceid,sensor_data.endpointid,max(timestamp) AS timestamp,interval_time
      FROM iot.sensor_data sensor_data INNER JOIN
      (SELECT deviceid,type FROM iot.box_info GROUP BY deviceid,type) device
      ON sensor_data.deviceid = device.deviceid
      INNER JOIN iot.box_type_info box_type_info ON device.type = box_type_info.id
      group by sensor_data.deviceid, interval_time, sensor_data.endpointid) A
    LOOP
      /* 获取箱子当前温度、湿度等数据 */
      SELECT temperature,humidity,longitude,latitude,speed,collide FROM iot.sensor_data
      WHERE timestamp = data_record.timestamp AND deviceid = data_record.deviceid LIMIT 1
      INTO v_temperature,v_humidity,v_longitude,v_latitude,v_speed,v_collide;

      /* 获取箱子在告警表中记录等最后的状态 */
      SELECT id,alarm_status FROM iot.alarm_info
      WHERE deviceid = data_record.deviceid AND code = 6001 ORDER BY timestamp desc LIMIT 1
      INTO v_id,v_alarm_status;

      IF data_record.flag = 1 THEN
        SELECT order_info.carrierid
        FROM iot.box_order_relation box_order_relation
        INNER JOIN iot.order_info order_info
        ON box_order_relation.trackid = order_info.trackid
        WHERE box_order_relation.deviceid = data_record.deviceid
        GROUP BY order_info.carrierid LIMIT 1 INTO v_carrier;

        IF v_alarm_status IS NULL OR v_alarm_status = 0 THEN
          /* 告警表中无或告警表中已有数据且处于清除状态 */
          INSERT INTO iot.alarm_info(timestamp,
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
                                     robert_operation_status,
                                     alarm_status,
                                     endpointid) VALUES
            (data_record.timestamp,
             data_record.deviceid,
             2,            /* 告警级别：1.通知 2.告警 3.错误 4.严重 */
             6001,         /* 失联告警码: 6001  */
             '在运',
             v_carrier,
             v_longitude,
             v_latitude,
             v_speed,
             v_temperature,
             v_humidity,
             v_collide,
             1,
             0.8,
             '装货',
             1,
             data_record.endpointid);

        ELSEIF v_alarm_status = 1 THEN
          /* 告警表中已有告警，且是未清除状态 */
          UPDATE iot.alarm_info SET timestamp = data_record.timestamp,
            level = 2,
            carrier = v_carrier,
            longitude = v_longitude,
            latitude = v_latitude,
            speed = v_speed,
            temperature =v_temperature,
            humidity = v_humidity,
            num_of_collide = v_collide,
            num_of_door_open = 1,
            battery = 0.8,
            robert_operation_status = '装货',
            alarm_status = 1
            WHERE id = v_id;
        END IF;

      ELSE
        /* 计算后标志是未告警，查看告警表中是否有告警，如果有则将告警清除 */
        IF v_alarm_status = 1 THEN
          UPDATE iot.alarm_info SET timestamp = data_record.timestamp,
            level = 2,
            longitude = v_longitude,
            latitude = v_latitude,
            speed = v_speed,
            temperature = v_temperature,
            humidity = v_humidity,
            num_of_collide = v_collide,
            num_of_door_open = 1,
            battery = 0.8,
            robert_operation_status = '装货',
            alarm_status = 0
            WHERE id = v_id;
        END IF;
      END IF;

      /* RAISE WARNING 'to print:%',data_record.flag; */
    END LOOP;

  END;
$$ LANGUAGE 'plpgsql';



/***
根据给定指标名称，查询改指标24小时范围内指标值
调用示例: SELECT * FROM iot.fn_indicator_history(1497369600,1497456000,'temperature','ESP32_AI_001') AS (value DECIMAL, hour INTEGER);
 */
CREATE OR REPLACE FUNCTION iot.fn_indicator_history(start_time INTEGER, end_time INTEGER, indicator TEXT, deviceid TEXT) RETURNS SETOF RECORD AS $$
  DECLARE
    v_start_time                         INTEGER;
    v_end_time                           INTEGER;
    v_indicator                          TEXT;
    v_seconds_per_hour                   INTEGER;
    v_record                             RECORD;
    v_deviceid                           TEXT;
    v_sql                                TEXT;
    v_hours                              INTEGER;
    v_i                                  INTEGER;

  BEGIN
    v_start_time := $1;
    v_end_time := $2;
    v_indicator := $3;
    v_deviceid := $4;
    v_seconds_per_hour := 3600;
    v_hours := 24;
    v_i := 0;

    v_sql = 'SELECT CAST(AVG(' || v_indicator || ') AS DECIMAL(20, 2)),hour FROM(SELECT CASE';

    FOR i IN 0..v_hours-1 LOOP
      v_sql := v_sql || ' WHEN timestamp >= ' || v_start_time || ' + ' || v_seconds_per_hour || ' * ' || i ||
                          ' AND timestamp < ' || v_start_time || ' + ' || v_seconds_per_hour || ' * ' || i+1 || ' THEN ' || i || ' ';
    END LOOP;

    v_sql := v_sql || 'END AS hour,CAST(' || v_indicator ||
      ' AS NUMERIC) FROM iot.sensor_data sensor_data WHERE timestamp >= ' || v_start_time ||' AND timestamp < ' || v_end_time ||
      ' AND sensor_data.deviceid = ''' || v_deviceid || ''') A GROUP BY hour ORDER BY hour ASC';

    RAISE WARNING 'to print:%',v_sql;

    FOR v_record IN EXECUTE v_sql LOOP
      RETURN NEXT v_record;
    END LOOP;

    RETURN;

  END;
$$ LANGUAGE 'plpgsql';
