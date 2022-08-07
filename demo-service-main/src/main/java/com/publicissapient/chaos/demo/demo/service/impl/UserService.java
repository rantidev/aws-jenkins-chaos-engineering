package com.publicissapient.chaos.demo.demo.service.impl;

import com.publicissapient.chaos.demo.demo.model.User;
import com.publicissapient.chaos.demo.demo.repositories.UserRepository;
import com.publicissapient.chaos.demo.demo.service.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService implements IUserService {

	@Autowired
	private UserRepository userRepository;

	@Autowired
	private RedisTemplate<String, String> redisTemplate;


	@Override
	public Optional<User> getUserById(String id) {
		return userRepository.findById(id);
	}

	@Override
	public User createUser(User user) {
		return userRepository.save(user);
	}

	@Override
	public User updateUser(String id, User user) {
		Optional<User> userEntity = userRepository.findById(id);
		if(userEntity.isPresent()){
			User tempUser = userEntity.get();
			tempUser.setUsername(user.getUsername());
			tempUser.setEmail(user.getEmail());
			tempUser.setName(user.getName());
			return userRepository.save(tempUser);
		}
		return null;
	}

	public List<User> getAllUsers(){
		return this.userRepository.findAll();
	}

	@Override
	public void deleteUser(User user) {
		userRepository.delete(user);
	}

}
