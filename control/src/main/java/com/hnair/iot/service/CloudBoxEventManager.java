package com.hnair.iot.service;

import com.hnair.iot.bee.client.*;
import com.hnair.iot.bee.client.event.registration.UserAttachCallback;
import com.hnair.iot.bee.client.like.family.ExhibitionEventFamily;
import com.hnair.iot.bee.client.like.family.event.CtrlCommand;
import com.hnair.iot.bee.client.like.family.event.CtrlResult;
import com.hnair.iot.bee.client.like.notification.DeviceNotification;
import com.hnair.iot.bee.client.like.profile.DeviceProfile;
import com.hnair.iot.bee.client.like.profile.NetworkType;
import com.hnair.iot.bee.client.notification.NotificationListener;
import com.hnair.iot.bee.client.notification.NotificationTopicListListener;
import com.hnair.iot.bee.client.notification.UnavailableTopicException;
import com.hnair.iot.bee.client.profile.ProfileContainer;
import com.hnair.iot.bee.common.endpoint.gen.SyncResponseResultType;
import com.hnair.iot.bee.common.endpoint.gen.Topic;
import com.hnair.iot.bee.common.endpoint.gen.UserAttachResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.hnair.iot.util.*;
import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import redis.clients.jedis.Jedis;
import static java.lang.Thread.sleep;
import org.json.JSONObject;

/**
 * Created by yuchunshen on 07/06/2017.
 */
public class CloudBoxEventManager {

    private static final Logger LOG = LoggerFactory.getLogger(CloudBoxEventManager.class);
    private BeeClient beeClient;
    private ExhibitionEventFamily ecf;
    private DeviceProfile profile = new DeviceProfile();
    private String derviceGroup = "68967072625541302123";
    private static String userId;
    private static String userAccessToken;
    private static String deviceName;

    static {
        try {
            Properties pro = new Properties();
            String filename = "user.properties";
            ClassLoader clsLoader = CloudBoxEventManager.class.getClassLoader();
            InputStreamReader in = new InputStreamReader(clsLoader.getResourceAsStream(filename), "UTF-8");
            pro.load(in);
            userId = pro.getProperty("iot.cloudbox.agent.user.id");
            userAccessToken = pro.getProperty("iot.cloudbox.agent.user.access.token");
            deviceName = pro.getProperty("iot.cloudbox.agent.device.name");
            in.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    public void start() throws IOException, InterruptedException {
        BeeClientPlatformContext context = new DesktopBeePlatformContext();
        final CountDownLatch startupLatch = new CountDownLatch(1);
        beeClient = Bee.newClient(context, new BeeClientStateAdapter() {
            @Override
            public void onStarted() {
                LOG.info("Client started");
                startupLatch.countDown();
            }

            @Override
            public void onStopped() {
                LOG.info("Client stopped");
            }
        });

        profile.setSerialNumber(DeviceUtil.getDeviceSN());
        profile.setName(deviceName);
        profile.setNetworkType(NetworkType.Ethernet);
        profile.setOs(DeviceUtil.getDeviceInfo());
        profile.setDescription(DeviceUtil.getDeviceName());
        // profile.setGroup(derviceGroup);
        LOG.info("Client profile: {}", profile);
        beeClient.setProfileContainer(new ProfileContainer() {
            @Override
            public DeviceProfile getProfile() {
                return profile;
            }
        });

        // Start the client and connect it to the server.
        beeClient.start();
        startupLatch.await();
        beeClient.updateProfile();
        beeClient.syncTopicsList();
        beeClient.addTopicListListener(new NotificationTopicListListener() {
            @Override
            public void onListUpdated(List<Topic> list) {

                List<Long> topicIds = new ArrayList<>();

                for (Topic topic : list) {

                    topicIds.add(topic.getId());

                }
                if (topicIds.size() > 0) {
                    try {
                        beeClient.subscribeToTopics(topicIds);
                    } catch (UnavailableTopicException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                    ;

                }
                LOG.info("onListUpdated: {}", list);
            }

        });

        beeClient.addNotificationListener(new NotificationListener() {
            @Override
            public void onNotification(long topicId, DeviceNotification notification) {
                LOG.info("notificr:" + notification + ":" + topicId);
            }
        });

        ecf = beeClient.getEventFamilyFactory().getExhibitionEventFamily();

        ecf.addListener(new ExhibitionEventFamily.Listener() {
            public void onEvent(CtrlResult event, String senderId) {
                // check Id
                LOG.info("event:" + event);
                String id = event.getId();
                if (!derviceGroup.equals(id)) {
                    //ecf.sendEvent(event, senderId);
                }
            }

            public void onEvent(CtrlCommand command, String source) {
                // TODO Auto-generated method stub
                LOG.info("event:" + command);
            }
        });
    }


    /***
     * attach
     * @param userId
     * @param userAccessToken
     */
    public void attachToUser(String userId, String userAccessToken) {
        try {
            final CountDownLatch attachLatch = new CountDownLatch(1);
            beeClient.attachUser(userId, userAccessToken, new UserAttachCallback() {
                @Override
                public void onAttachResult(UserAttachResponse response) {
                    if (response.getResult() == SyncResponseResultType.SUCCESS) {
                        LOG.info("onAttachResultresponse:" + response);
                        LOG.info("call back");
                    } else {
                        LOG.info("onAttachResultfailresponse:" + response);
                    }
                    attachLatch.countDown();
                }
            });
            attachLatch.await();
        } catch (InterruptedException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }


    /***
     * 通过CtrlCommand方式下发命令
     */
    public void sendByCtrlCommand() {
        String service = "";
        String action = "";
        String id = "";
        String data = "";

        CtrlCommand command = new CtrlCommand(service, action, id, data);
        ecf.sendEventToAll(command);
    }


    /***
     * 通过CtrlResult方式下发命令
     */
    public void sendByCtrlResult(String cmd) throws Exception{
        JSONObject jsonCmd = new JSONObject(cmd);

        String service = jsonCmd.getString("service");
        String action = jsonCmd.getString("action");
        String result = jsonCmd.getString("result");
        String id = jsonCmd.getString("id");

        CtrlResult command = new CtrlResult(service, action, result, id);
        if (null == id || id.isEmpty()){
            ecf.sendEventToAll(command);
        }
        else
            ecf.sendEvent(command, id);

        LOG.info("send command id: " + id);
    }


    public static void main(String[] args) throws IOException, InterruptedException {
        CloudBoxEventManager manager = new CloudBoxEventManager();
        manager.start();
        manager.attachToUser(userId, userAccessToken);

        Jedis jedis = new Jedis("127.0.0.1");
        String key = "command_list";

        while (true){
            sleep(10 * 1000);          //每隔10秒请求一次
            try {
                Long len = jedis.llen(key);
                if (len > 0){
                    for (int i=0;i<len;i++){
                        String value = jedis.lpop(key);
                        manager.sendByCtrlResult(value);
                    }
                }
            }
           catch (Exception e){
               LOG.error("send command error, msg: " + e.getMessage());
           }
        }
    }
}
