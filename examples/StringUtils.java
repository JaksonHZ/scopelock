package com.example.utils;

public class StringUtils {
    /**
     * Converte texto em slug legível para URL.
     */
    public static String slugifyText(String text) {
        return text.toLowerCase().trim().replaceAll("[^a-z0-9]+", "-");
    }

    public static String formatCurrencyBRL(double amount) {
        return String.format("R$ %.2f", amount);
    }
}
