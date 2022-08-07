package com.publicissapient.chaos.demo.demo.resource;


import com.publicissapient.chaos.demo.demo.service.KafkaMessagePublisher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class MessageResource {
	private static final Logger LOGGER = LoggerFactory.getLogger(MessageResource.class);

	@Value("${spring.redis.key}")
	private String key;

	@Autowired
	private RedisTemplate redisTemplate;

	@Autowired
	private KafkaMessagePublisher kafkaMessagePublisher;

	@GetMapping("/publish/{message}")
	public String publishMessage(@PathVariable("message")
								 final String message)
	{
		this.kafkaMessagePublisher.sendMessage(message);
		this.redisTemplate.opsForSet().add(key, message);
		return "Published Successfully";
	}



}

