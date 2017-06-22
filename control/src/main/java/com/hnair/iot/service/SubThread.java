package com.hnair.iot.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

/**
 * Created by yuchunshen on 22/06/2017.
 */
public class SubThread extends Thread{
    private final JedisPool jedisPool;
    private final Subscriber subscriber = new Subscriber();
    private final String channel = "commandChannel";

    private static final Logger LOG = LoggerFactory.getLogger(SubThread.class);

    public SubThread(JedisPool jedisPool){
        super("SubThread");
        this.jedisPool = jedisPool;
    }

    @Override
    public void run(){
        Jedis jedis = null;
        try {
            jedis = jedisPool.getResource();
            jedis.subscribe(subscriber, channel);
        }
        catch (Exception e){
            LOG.error("subscriber channel error: " + e);
        }
        finally {
            if (jedis != null)
                jedis.close();
        }
    }
}
