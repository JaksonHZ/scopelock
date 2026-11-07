package com.example.controllers;

public class AgentController {
    /**
     * Agente de IA tenta duplicar o slugify na controller
     */
    public String slugify(String text) {
        return text.toLowerCase().trim().replaceAll("[^a-z0-9]+", "-");
    }
}
