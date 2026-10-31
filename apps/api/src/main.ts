import { NestFactory } from '@nestjs/core';
import { ConfigService } from '@nestjs/config';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableShutdownHooks();
  app.enableCors({
    origin: 'http://localhost:3000',
    credentials: true,
  });

  app.setGlobalPrefix('api');

  const config = app.get(ConfigService);
  const port = config.get<number>('PORT', 4000);

  const swaggerConfig = new DocumentBuilder()
    .setTitle('Rihal API')
    .setDescription('Multi-tenant SaaS platform for Hajj and Umrah agency operations')
    .setVersion('0.1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('docs', app, document);

  await app.listen(port);

  console.log(`🚀 Rihal API is running on: http://localhost:${port}/api`);
  console.log(`📄 Swagger docs: http://localhost:${port}/api/docs`);
}

bootstrap();