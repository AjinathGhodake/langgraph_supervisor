package com.example.myapp.service;

import com.example.myapp.model.Character;
import com.example.myapp.repository.CharacterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.transaction.Transactional;
import java.util.Map;

@Service
public class ApsAdminComplianceService {

    @Autowired
    private CharacterRepository characterRepository;

    @Transactional
    public String saveAdminCompliance(Map<String, Object> data) throws Exception {
        Long characterId = Long.valueOf(data.get("character_id").toString());
        Character character = characterRepository.findById(characterId)
                .orElseThrow(() -> new Exception("Character not found"));

        // Assuming version and compliance agreement number are set here
        character.setVersion((Integer) data.get("version"));
        character.setSiteAdminComplianceAgreement("compliance_agreement_number_admin");

        characterRepository.save(character);

        if ((Boolean) data.get("is_preferred_org_save")) {
            // Save preferred organization logic here
        }

        return "Compliance saved successfully";
    }
}