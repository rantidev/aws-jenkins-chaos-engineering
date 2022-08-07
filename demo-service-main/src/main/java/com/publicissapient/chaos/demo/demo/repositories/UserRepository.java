package com.publicissapient.chaos.demo.demo.repositories;


import com.publicissapient.chaos.demo.demo.model.User;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends MongoRepository <User, String> {
}
