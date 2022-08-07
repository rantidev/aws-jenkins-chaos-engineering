package com.publicissapient.chaos.demo.demo.resource;

import com.publicissapient.chaos.demo.demo.model.User;
import com.publicissapient.chaos.demo.demo.service.IUserService;
import com.publicissapient.chaos.demo.demo.service.KafkaMessagePublisher;

import org.apache.kafka.common.errors.ResourceNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class UserResource {
	private static final Logger LOGGER = LoggerFactory.getLogger(UserResource.class);


	@Autowired
	private KafkaMessagePublisher kafkaMessagePublisher;

	@Autowired
	private IUserService iUserService;

	@GetMapping("/users")
	public ResponseEntity<List<User>> getAllUser(){
		return ResponseEntity.ok().body(iUserService.getAllUsers());
	}

	@GetMapping("/users/{id}")
	public ResponseEntity<User> getUser(@PathVariable(value = "id") String id) throws ResourceNotFoundException{
		User user = iUserService.getUserById(id)
				.orElseThrow(() -> new ResourceNotFoundException("User not found with the id :" + id));
		return ResponseEntity.ok().body(user);
	}

	@PostMapping("/users")
	public ResponseEntity<User> createUser(@RequestBody User user) {

		User createdUser =  iUserService.createUser(user);
		kafkaMessagePublisher.sendMessage(user.toString());
		return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
	}

	@PutMapping("/users/{id}")
	public ResponseEntity < User > updateUser(@PathVariable(value = "id") String id,
													  @RequestBody User user) throws ResourceNotFoundException {
		return ResponseEntity.ok(iUserService.updateUser(id, user));
	}

	@DeleteMapping("/users/{id}")
	public Map<String , Boolean> deleteUser(@PathVariable(value = "id") String id) throws ResourceNotFoundException {
		User user = iUserService.getUserById(id)
				.orElseThrow(() -> new ResourceNotFoundException("User not found with the id :" + id));

		iUserService.deleteUser(user);
		Map < String, Boolean > response = new HashMap< >();
		response.put("user deleted", Boolean.TRUE);
		return response;
	}
}
