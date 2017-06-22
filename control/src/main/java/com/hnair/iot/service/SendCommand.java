package com.hnair.iot.service;

import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.io.IOException;

/**
 * Created by yuchunshen on 22/06/2017.
 */
public class SendCommand {

    public static void main(String args[]){
        String redisIp = "127.0.0.1";
        int redisPort = 6379;
        JedisPool jedisPool = new JedisPool(new JedisPoolConfig(), redisIp, redisPort);
        SubThread thread = new SubThread(jedisPool);
        thread.start();
    }

}
