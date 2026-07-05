  FROM python:3.11-slim                                                                                                                                               
                                                                                                                                                                      
  WORKDIR /app                                                                                                                                                        
                                                                                                                                                                      
  COPY requirements.txt .                                                                                                                                             
  RUN pip install --no-cache-dir flask-jwt-extended gunicorn && \                                                                                                     
      pip install --no-cache-dir -r requirements.txt                                                                                                                  
                                                                                                                                                                      
  COPY . .                                                                                                                                                            
                                                                                                                                                                      
  RUN mkdir -p uploads uploads/heatmaps uploads/reports instance                                                                                                      
                                                                                                                                                                      
  EXPOSE 7860                                                                                                                                                         
                                                                                                                                                                      
  ENV FLASK_APP=backend/app.py                                                                                                                                        
                                                                                                                                                                      
  CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "backend", "app:app"]                                                                                         
  EOF
