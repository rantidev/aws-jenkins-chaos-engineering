package com.publicissapient.chaos.demo.demo.service;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class KafkaMessageConsumer {

    private static final Logger LOGGER = LoggerFactory.getLogger(KafkaMessageConsumer.class);

    @Value("${spring.redis.key}")
    private String key;

    @Autowired
    private RedisTemplate redisTemplate;

    @KafkaListener(topics = "${kafka.topicName}", groupId = "${kafka.groupId}")
    public void receive(ConsumerRecord<?, ?> consumerRecord) {
        LOGGER.info("received payload='{}'", consumerRecord.toString());
        this.redisTemplate.opsForSet().add(key, consumerRecord.value());

    }

}
