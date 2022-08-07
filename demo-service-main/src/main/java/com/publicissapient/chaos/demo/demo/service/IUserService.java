package com.publicissapient.chaos.demo.demo.service;

import com.publicissapient.chaos.demo.demo.model.User;


import java.util.List;
import java.util.Optional;

public interface IUserService {
	List<User> getAllUsers();;
	Optional<User> getUserById(String id);
	User createUser(User user);
	User updateUser(String id, User user);
	void deleteUser(User user);
}
