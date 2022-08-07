package com.publicissapient.chaos.demo.demo.resource;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;

@RestController
@RequestMapping("/api/v1")
public class CacheResource {
	private static final Logger LOGGER = LoggerFactory.getLogger(CacheResource.class);

	@Value("${spring.redis.key}")
	private String key;

	@Autowired
	private RedisTemplate redisTemplate;

	@GetMapping("/cache")
	public Set getAllCachedMessages()
	{
		return this.redisTemplate.opsForSet().members(key);
	}



}
