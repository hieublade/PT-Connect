package com.PTconnect.backend.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        Path uploadDir = Paths.get("uploads");
        String uploadPath = uploadDir.toFile().getAbsolutePath().replace("\\", "/");
        String parentUpload = Paths.get("..", "uploads").toFile().getAbsolutePath().replace("\\", "/");
        String fePublicUpload = Paths.get("..", "frontend-react", "public", "uploads").toFile().getAbsolutePath().replace("\\", "/");
        String feLocalUpload = Paths.get("frontend-react", "public", "uploads").toFile().getAbsolutePath().replace("\\", "/");

        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(
                        "file:" + uploadPath + "/",
                        "file:" + parentUpload + "/",
                        "file:" + fePublicUpload + "/",
                        "file:" + feLocalUpload + "/"
                );
    }
}
