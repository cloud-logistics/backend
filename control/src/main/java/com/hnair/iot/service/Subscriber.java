package com.hnair.iot.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import redis.clients.jedis.JedisPubSub;

/**
 * Created by yuchunshen on 21/06/2017.
 */
public class Subscriber extends JedisPubSub{

    private static final Logger LOG = LoggerFactory.getLogger(Subscriber.class);


    @Override
    public void onMessage(String channel, String message){
        LOG.info("channel:" + channel + ",receive msg:" + message);

        try {
            CloudBoxEventManager manager = new CloudBoxEventManager();
            String userId = "like.user";
            String userAccessToken = "like.token";
            manager.start();
            manager.attachToUser(userId, userAccessToken);
            manager.sendByCtrlResult(message);
        }
        catch (Exception e){
            LOG.error("send command error, msg: " + e.getMessage());
        }
    }

    @Override
    public void onSubscribe(String channel, int subscribedChannels){
        LOG.info("subscribe redis channel success, channel: "
                + channel + ",subscribedChannels: " + subscribedChannels);
    }

    @Override
    public void onUnsubscribe(String channel, int subscribedChannels){
        LOG.info("unsubscribe redis channel success, channel: "
                + channel + ", subscribedChannels: " + subscribedChannels);
    }
}
